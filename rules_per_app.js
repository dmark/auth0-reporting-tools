function (user, context, callback) {
  var audience = '';
  audience = audience ||
    (context.request && context.request.query && context.request.query.audience) ||
    (context.request && context.request.body && context.request.body.audience);
  if (audience === 'https://[YOUR_TENANT].auth0.com/api/v2/') {
    // The application must have "ManagementAPIAccess = True" in application metadata
    var client_authorized = context.clientMetadata && context.clientMetadata.ManagementAPIAccess === "True";
    user.app_metadata = user.app_metadata || {};
    // Authorized users must have:
    //  "app_metadata": { "roles": ["ManagementAPIAccess"]}
    var user_authorized = user.app_metadata.roles.indexOf('ManagementAPIAccess') !== -1;
    if (client_authorized && user_authorized) {
      // Specify the scopes you want to allow here.
      context.accessToken.scope = "read:rules read:clients";
      callback(null, user, context);
    } else {
      callback(new UnauthorizedError('Access denied'));
    }
  } else {
    callback(null, user, context);
  }
}