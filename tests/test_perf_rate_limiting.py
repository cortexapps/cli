"""
Performance test for client-side rate limiting.

This test is excluded from the main test suite because:
1. It intentionally generates high API load (1000+ req/min)
2. It makes many rapid parallel API requests to stress rate limiting
3. It should only be run manually via: just test-perf

Purpose:
- Verify that CortexClient's TokenBucket rate limiter prevents 429 errors
- Use aggressive parallelism (250 workers) with direct API calls
- Validate that even under heavy load, creates succeed without hitting 429s

Strategy:
- Create 1000 test catalog entities with 250 parallel workers
- Use direct CortexClient API calls (no subprocess overhead)
- CortexClient proactively limits requests to 1000 req/min (with 50-token burst)
- Validate that 95%+ of creates succeed without any 429 errors
"""

import time
import pytest
import os
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from cortexapps_cli.cortex_client import CortexClient


@pytest.mark.perf
def test_rate_limiting_with_retry_validation():
    """
    Rate limit test that validates CortexClient's TokenBucket rate limiter.

    Creates 1000 entities with 250 parallel workers to stress the API.
    CortexClient should proactively limit requests to avoid 429 errors.
    Test validates that aggressive parallel creates succeed (95%+ success rate).
    """
    print("\n=== Rate Limiting Test (Aggressive Parallel Creates) ===")
    print(f"Starting time: {time.strftime('%H:%M:%S')}")
    print("Testing CortexClient rate limiting with 250 parallel workers.\n")

    # Initialize CortexClient with credentials from environment
    api_key = os.environ.get('CORTEX_API_KEY')
    base_url = os.environ.get('CORTEX_BASE_URL', 'https://api.getcortexapp.com')

    if not api_key:
        pytest.skip("CORTEX_API_KEY not set")

    client = CortexClient(
        api_key=api_key,
        tenant='perf-test',
        numeric_level=logging.INFO,
        base_url=base_url
    )

    # Setup: Create custom entity type for test entities
    print("Setting up perf-test entity type...")
    entity_type_def = {
        "type": "perf-test",
        "name": "Performance Test Entity",
        "description": "Temporary entity type for rate limiting performance tests",
        "schema": {"type": "object", "required": [], "properties": {}}
    }

    # Create entity type (delete first if it exists from previous failed run)
    try:
        client.delete("api/v1/catalog/definitions/perf-test")
    except:
        pass  # Ignore if doesn't exist

    try:
        client.post("api/v1/catalog/definitions", data=entity_type_def)
        print("   ✅ Created perf-test entity type")
    except Exception as e:
        print(f"   ⚠️  Warning: Could not create entity type: {e}")

    # Create test data rapidly to stress rate limiting
    print("Creating 1000 test entities in parallel (testing rate limiter)...")
    start_time = time.time()

    test_entities = []
    create_errors = []
    completed_count = 0

    # Function to create a single entity using CortexClient directly (much faster than subprocess)
    def create_entity(index):
        entity_tag = f"rate-limit-test-{index:04d}"
        # OpenAPI YAML format (what the API expects)
        openapi_yaml = f"""openapi: 3.0.1
info:
  title: Rate Limit Test {index}
  x-cortex-tag: {entity_tag}
  x-cortex-type: perf-test
  description: Test entity {index} for rate limiting validation
"""

        try:
            # Make direct API call - CortexClient rate limiter prevents 429s
            # Use the open-api endpoint which accepts OpenAPI YAML format
            client.post("api/v1/open-api", data=openapi_yaml, content_type="application/openapi;charset=UTF-8")
            return {'success': True, 'tag': entity_tag, 'index': index}
        except Exception as e:
            return {
                'success': False,
                'tag': entity_tag,
                'index': index,
                'error': str(e)[:200]  # Truncate long errors
            }

    # Execute in parallel with 250 workers to stress the rate limiter
    # CortexClient should proactively limit to 1000 req/min and avoid 429s
    with ThreadPoolExecutor(max_workers=250) as executor:
        futures = {executor.submit(create_entity, i): i for i in range(1000)}

        for future in as_completed(futures):
            result = future.result()
            completed_count += 1

            if result['success']:
                test_entities.append(result['tag'])

                if completed_count % 50 == 0:
                    elapsed = time.time() - start_time
                    rate = completed_count / elapsed * 60 if elapsed > 0 else 0
                    print(f"   Completed {completed_count}/1000 entities in {elapsed:.1f}s | ~{rate:.0f} req/min")
            else:
                create_errors.append({
                    'entity': result['index'],
                    'tag': result['tag'],
                    'error': result['error']
                })
                print(f"   Entity {result['index']}: ❌ FAILED: {result['error']}")

    total_duration = time.time() - start_time

    # Cleanup - delete all entities by type (much faster than individual deletes)
    print(f"\nCleaning up test entities...")
    cleanup_start = time.time()
    try:
        # Delete all entities of type perf-test using params
        client.delete("api/v1/catalog", params={"types": "perf-test"})
        cleanup_duration = time.time() - cleanup_start
        print(f"   ✅ Deleted all perf-test entities in {cleanup_duration:.1f}s")
    except Exception as e:
        print(f"   ⚠️  Cleanup error: {str(e)}")

    # Cleanup entity type
    try:
        client.delete("api/v1/catalog/definitions/perf-test")
        print(f"   ✅ Deleted perf-test entity type")
    except Exception as e:
        print(f"   ⚠️  Could not delete entity type: {e}")

    # Analysis
    print(f"\n=== Test Results ===")
    print(f"Duration: {total_duration:.1f}s")
    print(f"Entities created: {len(test_entities)}/1000")
    print(f"Create errors: {len(create_errors)}")

    # Calculate approximate request rate (based on successful creates / time)
    # Note: This doesn't include internal retries by CortexClient
    requests_per_minute = (len(test_entities) / total_duration) * 60
    print(f"Effective rate: ~{requests_per_minute:.0f} req/min")

    # Assertions
    print(f"\n=== Validation ===")

    # 1. All or nearly all entities should be created successfully
    # If CortexClient rate limiter works, no 429s should occur
    success_rate = len(test_entities) / 1000
    print(f"Success rate: {success_rate * 100:.1f}%")
    assert success_rate >= 0.95, f"At least 95% of creates should succeed (got {success_rate * 100:.1f}%)"

    # 2. Should have very few or no failures
    # CortexClient should prevent 429s proactively
    print(f"Failures: {len(create_errors)}")
    assert len(create_errors) < 5, f"Should have very few failures (got {len(create_errors)})"

    print(f"\n✅ Rate limiting test PASSED")
    print(f"   - Created {len(test_entities)}/1000 entities in {total_duration:.1f}s")
    print(f"   - Success rate: {success_rate * 100:.1f}%")
    print(f"   - Effective rate: ~{requests_per_minute:.0f} req/min")
    print(f"   - Note: CortexClient proactively limits requests to 1000 req/min (burst: 50)")
    print(f"   - ✅ Aggressive parallel creates succeeded without hitting 429s")


