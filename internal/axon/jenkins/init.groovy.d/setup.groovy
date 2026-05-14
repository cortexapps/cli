import jenkins.model.*
import hudson.security.*
import com.cloudbees.plugins.credentials.*
import com.cloudbees.plugins.credentials.domains.*
import org.jenkinsci.plugins.plaincredentials.impl.*
import hudson.util.Secret

def instance = Jenkins.getInstance()

// Mark setup wizard as complete
instance.setInstallState(jenkins.install.InstallState.INITIAL_SETUP_COMPLETED)

// Create admin user
def realm = new HudsonPrivateSecurityRealm(false)
realm.createAccount("admin", "admin")
instance.setSecurityRealm(realm)

// Allow logged-in users full control
def strategy = new FullControlOnceLoggedInAuthorizationStrategy()
strategy.setAllowAnonymousRead(false)
instance.setAuthorizationStrategy(strategy)

// Create cortex_api_token credential from CORTEX_API_KEY env var
def apiKey = System.getenv('CORTEX_API_KEY')
if (apiKey) {
    def store = SystemCredentialsProvider.getInstance().getStore()
    def credential = new StringCredentialsImpl(
        CredentialsScope.GLOBAL,
        "cortex_api_token",
        "Cortex API Key for workflow callbacks",
        Secret.fromString(apiKey)
    )
    store.addCredentials(Domain.global(), credential)
    println("Created cortex_api_token credential")
} else {
    println("WARNING: CORTEX_API_KEY not set, skipping credential creation")
}

instance.save()
