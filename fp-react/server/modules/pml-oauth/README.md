

# Sample config options

The following shows typical values expected for the various configuration options for PML-OAuth.

    let sampleConfigOptions = {
        appBaseURL: 'http://localhost:3000/', // URL to the app, with trailing slash
        appCallbackPath: 'auth/pml/callback', // path to use for OAuth callback, with no leading slash
        appLoggedOutPath: '#/loggedout' // path in the app to go to after logging out
        oAuthAuthorizationURL: 'https://test.pennmutual.com/oauth2/dialog/authorize', // external URL for user's browser
        oAuthClientID: 'framework', // app's user ID configured in OAuth
        oAuthClientSecret: 'We need a Paul-themed project name', // app's password in OAuth
        oAuthLogoutURL: 'https://test.pennmutual.com/oauth2/logout', // external URL for user's browser
        oAuthScopes: 'offline_access basic_access pml_data_access', // scopes of OAuth access requested of user
        oAuthTokenURL: 'http://oauth2orize-mo/oauth/token', // internal URL for server to server
        oAuthUserInfoURL: 'http://oauth2orize-mo/api/userinfo', // internal URL for server to server
        personaURL: 'https://iam-persona-mo.pennmutual.com/persona-service/user/userid/{{USERID}}?ctx=authz&appKey=framework', // {{USERID}} will be replaced user's ID
    }
