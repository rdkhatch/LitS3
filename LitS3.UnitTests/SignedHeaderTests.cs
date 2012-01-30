using System.Collections.Specialized;
using System.IO;
using System.Net;
using System.Runtime.Serialization;
using System.Threading;
using LitS3.UnitTests.Support;
using Microsoft.VisualStudio.TestTools.UnitTesting;

namespace LitS3.UnitTests
{
    /// Allows Clients to communicate authorized requests directly with Amazon S3 - without the Secret Key. By first requesting the App Server (which has the Secret Key) to sign the requests header values & generate an Authorization header.
    /// Much faster transfers to Amazon S3, because they are not proxied through an App Server.
    /// 
    /// Overview of Process:
    /// 1.) Client converts any S3Request (ie, AddObjectRequest) to SignedHeaderRequest
    /// 2.) Client --> sends SignedHeaderRequest --> to App Server
    /// 3.) App Server signs SignedHeaderRequest's header values using Secret Key. (If App Server permits request)
    /// 4.) Client --< receives SignedHeaderResponse --< from App Server
    /// 5.) Client applies new signed Headers to original S3Request
    /// 6.) Client --> sends S3Request --> directly to Amazon. Successfully.

    [TestClass]
    public class SignedHeaderTests : S3TestBase
    {
        static string testBucketName = "testbucket";

        [TestMethod]
        public void Test_Authorization_Request_Matches_Real_Authorization()
        {
            var fileName = "dummy filename";
            bucket.DeleteFile(fileName);

            var addRequest = bucket.CreateAddRequest(fileName);

            // Upload Real File
            Send(addRequest);
            bucket.AssertFileExists(fileName);

            // Get Real Authentication Header
            var realAuthHeader = addRequest.WebRequest.Headers[HttpRequestHeader.Authorization];

            // Create a Delay. Authorize method puts DateTime.Now into header. This will check for that.
            Thread.Sleep(500);
            var timeOfRequest = addRequest.WebRequest.Headers[S3Headers.AmazonDate];

            // Without the Secret Key - Let's see if we can't match the realAuthHeader!!
            var fakeRequest = bucket.CreateAddRequest_WithoutSecretKey(fileName);

            // Set correct time for request
            fakeRequest.WebRequest.Headers[S3Headers.AmazonDate] = timeOfRequest;

            // Build Authorization Request
            var authRequest = fakeRequest.BuildSignedHeaderRequest();

            // Get Authentication Header
            var authResponse = s3.ApproveSignedHeaderRequest(authRequest);

            // Apply Authorization to S3 Request
            fakeRequest.ApplySignedHeader(authResponse);

            var ourAuthHeader = fakeRequest.WebRequest.Headers[HttpRequestHeader.Authorization];

            // Authorization hashes should match!
            Assert.AreEqual(realAuthHeader, ourAuthHeader);

            // Upload - from Client!
            bucket.DeleteFile(fileName);
            Send(fakeRequest);
            bucket.AssertFileExists(fileName);

            // Show that our fakeRequest cannot be hijacked to do anything - other than what we've Authorized it for
            bool hijackPrevented = false;
            bucket.DeleteFile(fileName);
            fakeRequest.WebRequest.Method = "Delete";
            Send(fakeRequest);
            bucket.AssertFileDoesNotExist(fileName);
        }

        [TestMethod]
        public void Test_Authorization_Request_should_upload_to_Amazon()
        {
            var fileName = "serializedFileRequest.txt";
            bucket.DeleteFile(fileName);

            var addRequest = bucket.CreateAddRequest(fileName);

            // Serialize headers, etc. into Authorization Request
            var authRequest = addRequest.BuildSignedHeaderRequest();

            // Server - Authorizes. Build Response to send back to Client
            SignedHeaderResponse authResponse = s3.ApproveSignedHeaderRequest(authRequest);

            // Client - Applies Server's Authorization to S3 Request
            addRequest.ApplySignedHeader(authResponse);

            Send(addRequest);

            bucket.AssertFileExists(fileName);
        }

        [TestMethod]
        public void Test_Serialize_Authentication_Request_and_Response()
        {
            var addRequest = bucket.CreateAddRequest("dummy");

            // Serialize - Authentication Request
            var authRequest = addRequest.BuildSignedHeaderRequest();
            var authRequest2 = SerializeDeserialize(authRequest);

            Assert.AreEqual(authRequest.BucketName, authRequest2.BucketName);
            Assert.AreEqual(authRequest.ContentType, authRequest2.ContentType);
            Assert.AreEqual(authRequest.Method, authRequest2.Method);
            Assert.AreEqual(authRequest.RequestURI, authRequest2.RequestURI);
            AssertNameValueCollectionsEqual(authRequest.Headers, authRequest2.Headers);

            // Serialize - Authentication Response
            var authResponse = s3.ApproveSignedHeaderRequest(authRequest2);
            var authResponse2 = SerializeDeserialize(authResponse);

            Assert.AreEqual(authResponse.IsAuthorized, authResponse2.IsAuthorized);
            AssertNameValueCollectionsEqual(authResponse.Headers, authResponse2.Headers);

        }





        void AssertNameValueCollectionsEqual(NameValueCollection collection1, NameValueCollection collection2)
        {
            Assert.AreEqual(collection1.Count, collection2.Count);
            for (int i = 0; i < collection1.Count; i++)
            {
                var pair1Key = collection1.Keys[i];
                var pair2Key = collection2.Keys[i];
                Assert.AreEqual(pair1Key, pair2Key);

                var pair1Value = collection1[i];
                var pair2Value = collection2[i];
                Assert.AreEqual(pair1Value, pair2Value);
            }
        }



        static SignedHeaderRequest SerializeDeserialize(SignedHeaderRequest authRequest)
        {
            var serializer = new NetDataContractSerializer();
            var stream = new MemoryStream();
            serializer.Serialize(stream, authRequest);
            stream.Position = 0;
            var addRequest2 = (SignedHeaderRequest)serializer.Deserialize(stream);

            return addRequest2;
        }

        SignedHeaderResponse SerializeDeserialize(SignedHeaderResponse authResponse)
        {
            var serializer = new NetDataContractSerializer();
            var stream = new MemoryStream();
            serializer.Serialize(stream, authResponse);
            stream.Position = 0;
            var result = (SignedHeaderResponse)serializer.Deserialize(stream);

            return result;
        }

    }



}
