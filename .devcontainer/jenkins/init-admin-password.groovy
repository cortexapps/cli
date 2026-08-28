import hudson.model.User
import hudson.security.AuthorizationStrategy
import hudson.security.HudsonPrivateSecurityRealm
import jenkins.model.Jenkins

// Demo Codespace setup.
//
// Security model: Jenkins is fully unsecured (no auth required) with CSRF disabled.
// The Codespace URL (long random string) is the only access control — appropriate
// for a short-lived demo instance.  The admin user is still created with a known
// password so the Jenkins UI can be accessed interactively.

def instance = Jenkins.getInstance()

def realm = new HudsonPrivateSecurityRealm(false)
instance.setSecurityRealm(realm)

def user = User.get("admin")
def details = HudsonPrivateSecurityRealm.Details.fromPlainPassword("cortex-demo")
user.addProperty(details)
user.save()

// Unsecured: all requests (including anonymous POST from Cortex) are permitted.
// This bypasses the Codespace proxy stripping Authorization headers on POST.
instance.setAuthorizationStrategy(AuthorizationStrategy.UNSECURED)

// Disable CSRF so POST requests from Cortex don't need a crumb.
instance.setCrumbIssuer(null)

instance.save()
