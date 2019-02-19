// This rule provisions limited access to the Management API for authorized
// users and applications. IF the audience is the Management API AND the
// application (client) has "ManagementAPIAccess = True" in the application
// metadata, AND the user has '{ "roles": ["ManagementAPIAccess"]' } in their
// app_metadata, then the user is given the scopes listed in context.accessToken.scope.
//
// Replace YOUR_TENANT with the name of you tenant. Update context.accessToken.scope
// as needed.
function (user, context, callback) {
  var audience = '';
  audience = audience ||
    (context.request && context.request.query && context.request.query.audience) ||
    (context.request && context.request.body && context.request.body.audience);
  if (audience === 'https://[YOUR_TENANT].auth0.com/api/v2/') {
    var client_authorized = context.clientMetadata && context.clientMetadata.ManagementAPIAccess === "True";
    user.app_metadata = user.app_metadata || {};
    var user_authorized = user.app_metadata.roles.indexOf('ManagementAPIAccess') !== -1;
    if (client_authorized && user_authorized) {
      context.accessToken.scope = "read:rules read:clients";
      callback(null, user, context);
    } else {
      callback(new UnauthorizedError('Access denied'));
    }
  } else {
    callback(null, user, context);
  }
}