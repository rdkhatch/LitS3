using LitS3.UnitTests.Support;
using Microsoft.VisualStudio.TestTools.UnitTesting;

namespace LitS3.UnitTests
{
    [TestClass]
    public class BasicTests : S3TestBase
    {
        [TestMethod]
        public void Create_empty_file()
        {
            var fileName = "emptyfile.txt";
            bucket.DeleteFile(fileName);

            var addRequest = bucket.CreateAddRequest(fileName);
            Send(addRequest);

            bucket.AssertFileExists(fileName);
        }

        [TestMethod]
        public void Create_Text_File()
        {
            var fileName = "file2.txt";
            bucket.DeleteFile(fileName);

            var addRequest = bucket.CreateAddRequest(fileName);

            // File Contents
            addRequest.ContentType = "text/html";
            var fileContents = "this is a test uploaded string";

            // File Stream
            var fileStream = GetStreamFromString(fileContents);

            SendStream(addRequest, fileStream);
            bucket.AssertFileExists(fileName);

            var fileContentsAtS3 = bucket.GetObjectString(fileName);
            Assert.AreEqual(fileContents, fileContentsAtS3);
        }
    }
}
