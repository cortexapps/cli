import hudson.model.User
import hudson.security.FullControlOnceLoggedInAuthorizationStrategy
import hudson.security.HudsonPrivateSecurityRealm
import jenkins.model.Jenkins

// Configure security here — NOT in jenkins.yaml — to avoid JCasC recreating the security
// realm (which would discard the user set up below).  JCasC runs after init scripts, so
// any securityRealm / authorizationStrategy in jenkins.yaml would overwrite this.

def instance = Jenkins.getInstance()

def realm = new HudsonPrivateSecurityRealm(false)
instance.setSecurityRealm(realm)

// Get or create the admin user and set a known password.
// User.get(id) creates the user object if it doesn't exist; addProperty overwrites
// any existing HudsonPrivateSecurityRealm.Details (the password property).
def user = User.get("admin")
def details = HudsonPrivateSecurityRealm.Details.fromPlainPassword("cortex-demo")
user.addProperty(details)
user.save()

def strategy = new FullControlOnceLoggedInAuthorizationStrategy()
strategy.setAllowAnonymousRead(false)
instance.setAuthorizationStrategy(strategy)

instance.save()
