using System;
using System.Linq;
using Microsoft.VisualStudio.TestTools.UnitTesting;


namespace LitS3.UnitTests
{

    public class BucketContext
    {
        public string BucketName { get; set; }
        public S3Service Service { get; set; }
    }


    public static class BucketContextExtensions
    {
        public static void DeleteFile(this BucketContext bucket, string fileName)
        {
            bucket.Service.DeleteObject(bucket.BucketName, fileName);
        }

        public static void AssertFileExists(this BucketContext bucket, string fileName)
        {
            var match = bucket.Service.ListObjects(bucket.BucketName, fileName).OfType<ObjectEntry>().ToList();
            Assert.IsTrue(match.Count == 1);
            Assert.AreEqual(fileName, match.Single().Key);
        }

        public static void AssertFileDoesNotExist(this BucketContext bucket, string fileName)
        {
            var match = bucket.Service.ListObjects(bucket.BucketName, fileName).OfType<ObjectEntry>().ToList();
            Assert.IsTrue(match.Count == 0);
        }

        public static AddObjectRequest CreateAddRequest(this BucketContext bucket, string filename)
        {
            return CreateAddRequest(bucket.Service, bucket.BucketName, filename);
        }

        /// <summary>
        /// Creates AddRequest without knowledge of the SecretKey.  Used for testing SignedHeaderRequest/Response
        /// </summary>
        public static AddObjectRequest CreateAddRequest_WithoutSecretKey(this BucketContext bucket, string filename)
        {
            // Create Service without knowledge of the Secret Key
            var serviceWithoutKeys = new S3Service();

            return CreateAddRequest(serviceWithoutKeys, bucket.BucketName, filename);
        }


        static AddObjectRequest CreateAddRequest(S3Service service, string bucketName, string filename)
        {
            var addRequest = new AddObjectRequest(service, bucketName, filename);
            addRequest.ContentLength = 0;

            return addRequest;
        }


        public static string GetObjectString(this BucketContext bucket, string filename)
        {
            string contentType;
            return bucket.Service.GetObjectString(bucket.BucketName, filename, out contentType);
        }

        public static string GetObjectString(this BucketContext bucket, string filename, out string contentType)
        {
            return bucket.Service.GetObjectString(bucket.BucketName, filename, out contentType);
        }


        public static Uri GetAuthorizedUri(this BucketContext bucket, string filename, DateTime expires)
        {
            return bucket.Service.GetAuthorizedUri(bucket.BucketName, filename, expires);
        }


    }
}
