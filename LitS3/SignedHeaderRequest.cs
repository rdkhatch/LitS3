
using System.Net;
using System.Security;
namespace LitS3
{
    /// <summary>
    /// Allows Clients to communicate authorized requests directly with Amazon S3 - without the Secret Key. By first requesting the App Server (which has the Secret Key) to sign the requests header values & generate an Authorization header.
    /// Represents a client's request to have the Owner sign & authorize the S3Request's header values with the Secret Key
    /// </summary>
    public class SignedHeaderRequest
    {
        public string BucketName { get; set; }
        public string RequestURI { get; set; }
        public WebHeaderCollection Headers { get; set; }
        public string Method { get; set; }
        public string ContentType { get; set; }

    }

    /// <summary>
    /// Response from Owner with signed Authorization headers. Headers should be applied back to the S3Request.
    /// </summary>
    public class SignedHeaderResponse
    {
        public bool IsAuthorized { get; set; }
        public WebHeaderCollection Headers { get; set; }
    }


    public static class AuthorizationRequestExtensions
    {

        /// <summary>
        /// Client can convert any S3Request to a SignedHeaderRequest.  SignedHeaderRequest can be serialized & sent to App Server where it can be signed with the Secret Key.
        /// </summary>
        /// <param name="s3request"></param>
        /// <returns></returns>
        public static SignedHeaderRequest BuildSignedHeaderRequest(this S3Request s3request)
        {
            var httpRequest = s3request.WebRequest;

            var authRequest = new SignedHeaderRequest()
            {
                // Bucket
                BucketName = s3request.BucketName,

                // HTTP Stuff
                Headers = httpRequest.Headers,
                Method = httpRequest.Method,
                ContentType = httpRequest.ContentType,
                RequestURI = httpRequest.RequestUri.ToString()
            };

            return authRequest;
        }

        /// <summary>
        /// App Server uses this method to sign a SignedHeaderRequest with the Secret Key.  App Server sends SignedHeaderResponse back to Client.
        /// </summary>
        /// <param name="service"></param>
        /// <param name="authRequest"></param>
        /// <returns></returns>
        public static SignedHeaderResponse ApproveSignedHeaderRequest(this S3Service service, SignedHeaderRequest authRequest)
        {
            // Create matching HTTP Request, so we can authorize for our requestor
            var httpRequest = (HttpWebRequest)HttpWebRequest.Create(authRequest.RequestURI);
            httpRequest.Headers.Add(authRequest.Headers);
            httpRequest.Method = authRequest.Method;
            httpRequest.ContentType = authRequest.ContentType;

            // Authorize with Secret Key
            service.AuthorizeRequest(null, httpRequest, authRequest.BucketName);

            var authResponse = new SignedHeaderResponse()
            {
                Headers = httpRequest.Headers,
                IsAuthorized = true
            };

            return authResponse;
        }

        /// <summary>
        /// Client uses this method to apply a Signed Header to a S3Request. Allows Client to send an Authorized S3Request directly to Amazon - without the Secret Key.
        /// </summary>
        /// <param name="request"></param>
        /// <param name="authResponse"></param>
        public static void ApplySignedHeader(this S3Request request, SignedHeaderResponse authResponse)
        {
            if (authResponse.IsAuthorized == false)
                throw new SecurityException("Unable to apply AuthorizationResponse to S3Request. The S3 AuthenticationResponse you received was not authorized.");

            request.WebRequest.Headers.Clear();
            request.WebRequest.Headers.Add(authResponse.Headers);
        }
    }

}
