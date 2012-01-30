using System.IO;
using System.Text;
using LitS3.UnitTests.Configuration;
using Microsoft.VisualStudio.TestTools.UnitTesting;

namespace LitS3.UnitTests.Support
{
    [TestClass]
    public abstract class S3TestBase
    {
        protected S3Service s3;
        protected BucketContext bucket;

        [TestInitialize]
        public void TestInitializing()
        {
            InitTest(Settings.Default);
        }

        internal virtual void InitTest(Settings settings)
        {
            s3 = new S3Service()
            {
                AccessKeyID = settings.AccessKeyID,
                SecretAccessKey = settings.SecretAccessKey
            };

            bucket = new BucketContext() { BucketName = settings.TestBucketName, Service = s3 };
        }




        protected Stream GetStreamFromString(string fileContents)
        {
            UTF8Encoding encoding = new UTF8Encoding();
            var fileBytes = encoding.GetBytes(fileContents);

            return new MemoryStream(fileBytes);
        }

        protected void Send(AddObjectRequest addRequest)
        {
            var response = addRequest.GetResponse();
            response.Close();
        }

        protected void SendStream(AddObjectRequest addRequest, Stream fileStream)
        {
            addRequest.ContentLength = fileStream.Length;

            using (var outputStream = addRequest.GetRequestStream())
            {
                fileStream.CopyTo(outputStream);
            }

            Send(addRequest);
        }
    }
}
