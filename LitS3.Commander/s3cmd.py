# LitS3.Commander
# Command-line interface to LitS3
#
# The MIT License
# 
# Copyright (c) 2008, Nick Farina
#
# Author(s):
#
#   Atif Aziz, http://www.raboof.com/
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

# $Id: s3cmd.py 100 2009-07-25 10:40:08Z azizatif $

import sys, clr, re

from System import \
    DateTime, Int64, Byte, Array, Enum, Convert, Environment, PlatformID, \
    Uri, UriFormat, UriComponents, UriParser, GenericUriParser, GenericUriParserOptions
from System.IO import Path, FileInfo, Directory, MemoryStream, File
from System.Text import Encoding
from System.Environment import GetEnvironmentVariable

clr.AddReference("System.Security")
from System.Security.Cryptography import ProtectedData, DataProtectionScope, RNGCryptoServiceProvider

clr.AddReferenceToFile('LitS3.dll')
from LitS3 import *

MIME_MAP = {
    '.323'    : 'text/h323',
    '.asx'    : 'video/x-ms-asf',
    '.acx'    : 'application/internet-property-stream',
    '.ai'     : 'application/postscript',
    '.aif'    : 'audio/x-aiff',
    '.aiff'   : 'audio/aiff',
    '.axs'    : 'application/olescript',
    '.aifc'   : 'audio/aiff',
    '.asr'    : 'video/x-ms-asf',
    '.avi'    : 'video/x-msvideo',
    '.asf'    : 'video/x-ms-asf',
    '.au'     : 'audio/basic',
    '.bin'    : 'application/octet-stream',
    '.bas'    : 'text/plain',
    '.bcpio'  : 'application/x-bcpio',
    '.bmp'    : 'image/bmp',
    '.cdf'    : 'application/x-cdf',
    '.cat'    : 'application/vndms-pkiseccat',
    '.crt'    : 'application/x-x509-ca-cert',
    '.c'      : 'text/plain',
    '.css'    : 'text/css',
    '.cer'    : 'application/x-x509-ca-cert',
    '.crl'    : 'application/pkix-crl',
    '.cmx'    : 'image/x-cmx',
    '.csh'    : 'application/x-csh',
    '.cod'    : 'image/cis-cod',
    '.cpio'   : 'application/x-cpio',
    '.clp'    : 'application/x-msclip',
    '.crd'    : 'application/x-mscardfile',
    '.dll'    : 'application/x-msdownload',
    '.dot'    : 'application/msword',
    '.doc'    : 'application/msword',
    '.dvi'    : 'application/x-dvi',
    '.dir'    : 'application/x-director',
    '.dxr'    : 'application/x-director',
    '.der'    : 'application/x-x509-ca-cert',
    '.dib'    : 'image/bmp',
    '.dcr'    : 'application/x-director',
    '.disco'  : 'text/xml',
    '.exe'    : 'application/octet-stream',
    '.etx'    : 'text/x-setext',
    '.evy'    : 'application/envoy',
    '.eml'    : 'message/rfc822',
    '.eps'    : 'application/postscript',
    '.flr'    : 'x-world/x-vrml',
    '.fif'    : 'application/fractals',
    '.gtar'   : 'application/x-gtar',
    '.gif'    : 'image/gif',
    '.gz'     : 'application/x-gzip',
    '.hta'    : 'application/hta',
    '.htc'    : 'text/x-component',
    '.htt'    : 'text/webviewhtml',
    '.h'      : 'text/plain',
    '.hdf'    : 'application/x-hdf',
    '.hlp'    : 'application/winhlp',
    '.html'   : 'text/html',
    '.htm'    : 'text/html',
    '.hqx'    : 'application/mac-binhex40',
    '.isp'    : 'application/x-internet-signup',
    '.iii'    : 'application/x-iphone',
    '.ief'    : 'image/ief',
    '.ivf'    : 'video/x-ivf',
    '.ins'    : 'application/x-internet-signup',
    '.ico'    : 'image/x-icon',
    '.jpg'    : 'image/jpeg',
    '.jfif'   : 'image/pjpeg',
    '.jpe'    : 'image/jpeg',
    '.jpeg'   : 'image/jpeg',
    '.js'     : 'application/x-javascript',
    '.lsx'    : 'video/x-la-asf',
    '.latex'  : 'application/x-latex',
    '.lsf'    : 'video/x-la-asf',
    '.mhtml'  : 'message/rfc822',
    '.mny'    : 'application/x-msmoney',
    '.mht'    : 'message/rfc822',
    '.mid'    : 'audio/mid',
    '.mpv2'   : 'video/mpeg',
    '.man'    : 'application/x-troff-man',
    '.mvb'    : 'application/x-msmediaview',
    '.mpeg'   : 'video/mpeg',
    '.m3u'    : 'audio/x-mpegurl',
    '.mdb'    : 'application/x-msaccess',
    '.mpp'    : 'application/vnd.ms-project',
    '.m1v'    : 'video/mpeg',
    '.mpa'    : 'video/mpeg',
    '.me'     : 'application/x-troff-me',
    '.m13'    : 'application/x-msmediaview',
    '.movie'  : 'video/x-sgi-movie',
    '.m14'    : 'application/x-msmediaview',
    '.mpe'    : 'video/mpeg',
    '.mp2'    : 'video/mpeg',
    '.mov'    : 'video/quicktime',
    '.mp3'    : 'audio/mpeg',
    '.mpg'    : 'video/mpeg',
    '.ms'     : 'application/x-troff-ms',
    '.nc'     : 'application/x-netcdf',
    '.nws'    : 'message/rfc822',
    '.oda'    : 'application/oda',
    '.ods'    : 'application/oleobject',
    '.pmc'    : 'application/x-perfmon',
    '.p7r'    : 'application/x-pkcs7-certreqresp',
    '.p7b'    : 'application/x-pkcs7-certificates',
    '.p7s'    : 'application/pkcs7-signature',
    '.pmw'    : 'application/x-perfmon',
    '.ps'     : 'application/postscript',
    '.p7c'    : 'application/pkcs7-mime',
    '.pbm'    : 'image/x-portable-bitmap',
    '.ppm'    : 'image/x-portable-pixmap',
    '.pub'    : 'application/x-mspublisher',
    '.png'    : 'image/png',
    '.pnm'    : 'image/x-portable-anymap',
    '.pml'    : 'application/x-perfmon',
    '.p10'    : 'application/pkcs10',
    '.pfx'    : 'application/x-pkcs12',
    '.p12'    : 'application/x-pkcs12',
    '.pdf'    : 'application/pdf',
    '.pps'    : 'application/vnd.ms-powerpoint',
    '.p7m'    : 'application/pkcs7-mime',
    '.pko'    : 'application/vndms-pkipko',
    '.ppt'    : 'application/vnd.ms-powerpoint',
    '.pmr'    : 'application/x-perfmon',
    '.pma'    : 'application/x-perfmon',
    '.pot'    : 'application/vnd.ms-powerpoint',
    '.prf'    : 'application/pics-rules',
    '.pgm'    : 'image/x-portable-graymap',
    '.qt'     : 'video/quicktime',
    '.ra'     : 'audio/x-pn-realaudio',
    '.rgb'    : 'image/x-rgb',
    '.ram'    : 'audio/x-pn-realaudio',
    '.rmi'    : 'audio/mid',
    '.ras'    : 'image/x-cmu-raster',
    '.roff'   : 'application/x-troff',
    '.rtf'    : 'application/rtf',
    '.rtx'    : 'text/richtext',
    '.sv4crc' : 'application/x-sv4crc',
    '.spc'    : 'application/x-pkcs7-certificates',
    '.setreg' : 'application/set-registration-initiation',
    '.snd'    : 'audio/basic',
    '.stl'    : 'application/vndms-pkistl',
    '.setpay' : 'application/set-payment-initiation',
    '.stm'    : 'text/html',
    '.shar'   : 'application/x-shar',
    '.sh'     : 'application/x-sh',
    '.sit'    : 'application/x-stuffit',
    '.spl'    : 'application/futuresplash',
    '.sct'    : 'text/scriptlet',
    '.scd'    : 'application/x-msschedule',
    '.sst'    : 'application/vndms-pkicertstore',
    '.src'    : 'application/x-wais-source',
    '.sv4cpio': 'application/x-sv4cpio',
    '.tex'    : 'application/x-tex',
    '.tgz'    : 'application/x-compressed',
    '.t'      : 'application/x-troff',
    '.tar'    : 'application/x-tar',
    '.tr'     : 'application/x-troff',
    '.tif'    : 'image/tiff',
    '.txt'    : 'text/plain',
    '.texinfo': 'application/x-texinfo',
    '.trm'    : 'application/x-msterminal',
    '.tiff'   : 'image/tiff',
    '.tcl'    : 'application/x-tcl',
    '.texi'   : 'application/x-texinfo',
    '.tsv'    : 'text/tab-separated-values',
    '.ustar'  : 'application/x-ustar',
    '.uls'    : 'text/iuls',
    '.vcf'    : 'text/x-vcard',
    '.wps'    : 'application/vnd.ms-works',
    '.wav'    : 'audio/wav',
    '.wrz'    : 'x-world/x-vrml',
    '.wri'    : 'application/x-mswrite',
    '.wks'    : 'application/vnd.ms-works',
    '.wmf'    : 'application/x-msmetafile',
    '.wcm'    : 'application/vnd.ms-works',
    '.wrl'    : 'x-world/x-vrml',
    '.wdb'    : 'application/vnd.ms-works',
    '.wsdl'   : 'text/xml',
    '.xml'    : 'text/xml',
    '.xlm'    : 'application/vnd.ms-excel',
    '.xaf'    : 'x-world/x-vrml',
    '.xla'    : 'application/vnd.ms-excel',
    '.xls'    : 'application/vnd.ms-excel',
    '.xof'    : 'x-world/x-vrml',
    '.xlt'    : 'application/vnd.ms-excel',
    '.xlc'    : 'application/vnd.ms-excel',
    '.xsl'    : 'text/xml',
    '.xbm'    : 'image/x-xbitmap',
    '.xlw'    : 'application/vnd.ms-excel',
    '.xpm'    : 'image/x-xpixmap',
    '.xwd'    : 'image/x-xwindowdump',
    '.xsd'    : 'text/xml',
    '.z'      : 'application/x-compress',
    '.zip'    : 'application/x-zip-compressed',
    '.*'      : 'application/octet-stream',
    # Office 2007 MIME types
    # http://www.bram.us/2007/05/25/office-2007-mime-types-for-iis/
    'docm'    : 'application/vnd.ms-word.document.macroEnabled.12',
    'docx'    : 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'dotm'    : 'application/vnd.ms-word.template.macroEnabled.12',
    'dotx'    : 'application/vnd.openxmlformats-officedocument.wordprocessingml.template',
    'potm'    : 'application/vnd.ms-powerpoint.template.macroEnabled.12',
    'potx'    : 'application/vnd.openxmlformats-officedocument.presentationml.template',
    'ppam'    : 'application/vnd.ms-powerpoint.addin.macroEnabled.12',
    'ppsm'    : 'application/vnd.ms-powerpoint.slideshow.macroEnabled.12',
    'ppsx'    : 'application/vnd.openxmlformats-officedocument.presentationml.slideshow',
    'pptm'    : 'application/vnd.ms-powerpoint.presentation.macroEnabled.12',
    'pptx'    : 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
    'xlam'    : 'application/vnd.ms-excel.addin.macroEnabled.12',
    'xlsb'    : 'application/vnd.ms-excel.sheet.binary.macroEnabled.12',
    'xlsm'    : 'application/vnd.ms-excel.sheet.macroEnabled.12',
    'xlsx'    : 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    'xltm'    : 'application/vnd.ms-excel.template.macroEnabled.12',
    'xltx'    : 'application/vnd.openxmlformats-officedocument.spreadsheetml.template',
}

UriParser.Register(
    GenericUriParser(GenericUriParserOptions.NoQuery 
                     | GenericUriParserOptions.NoPort 
                     | GenericUriParserOptions.NoFragment 
                     | GenericUriParserOptions.NoUserInfo), 
    's3', 0)

def parse_s3uri(path):
    """Parses an S3 URI into its bucket and key constituents."""
    uri = Uri(path)
    return uri.Authority, uri.GetComponents(UriComponents.Path, UriFormat.Unescaped)

def copy_stream(source, dest, length):
    buffer = Array.CreateInstance(Byte, 8192)
    while length > 0:
        bytesRead = source.Read(buffer, 0, buffer.Length)
        if bytesRead > 0:
            dest.Write(buffer, 0, bytesRead)
        else:
            raise Exception("Unexpected end of stream while copying.")
        length -= bytesRead

def is_windows():
    return Environment.OSVersion.Platform in (PlatformID.Win32NT, PlatformID.Win32Windows, PlatformID.Win32S, PlatformID.WinCE)

def parse_options(args, names, flags = None, lax = False):
    args = list(args) # copy for r/w
    required = [name[:-1] for name in names if '!' == name[-1:]]
    all = [name.rstrip('!') for name in names]
    if flags:
        all.extend(flags)
    options = {}
    anon = []
    while args:
        arg = args.pop(0)
        if arg[:2] == '--':
            name = arg[2:]
            if not name: # comment
                break
            if not name in all:
                if not lax:
                    raise Exception('Unknown argument: %s' % name)
                anon.append(arg)
                continue
            if flags and name in flags:
                options[name] = True
            elif args:
                options[name] = args.pop(0)
            else:
                raise Exception('Missing argument value: %s' % name)
        else:
            anon.append(arg)
    for name in required:
        if not name in options:
            raise Exception('Missing required argument: %s' % name)
    return options, anon

def lax_parse_options(args, names, flags = None):
    return parse_options(args, names, flags, True)
    
def parse_canned_acl_arg(arg):
    return arg and Enum.Parse(CannedAcl, arg.replace('-', ''), True) or CannedAcl.Private

class S3Commander(object):

    def __init__(self, s3):
        self.s3 = s3

    def __call__(self, name, args):
        cmd = getattr(self, name.replace('del', 'rm').replace('ls', 'list'), None)
        if not cmd:
            raise Exception('Unknown command (%s).' % name)
        opt_specs = getattr(cmd, 'opt_specs', None)
        if opt_specs:
            flags = getattr(cmd, 'opt_flags', None)
            cmd(*reversed(parse_options(args, opt_specs, flags)))
        else:
            cmd(parse_options(args, ())[1])

    def mkbkt(self, args, options):
        """Creates a new bucket"""
        if not args:
            raise Exception('Missing bucket name.')
        bucket = args.pop(0)
        if options.get('europe', False):
            self.s3.CreateBucketInEurope(bucket)
        else:
            self.s3.CreateBucket(bucket)

    mkbkt.opt_specs = ('europe', )
    mkbkt.opt_flags = ('europe', )

    def rmbkt(self, args):
        """Deletes a bucket"""
        if not args:
            raise Exception('Missing bucket name.')
        self.s3.DeleteBucket(args.pop(0))
 
    def list(self, args, options):
        """Lists all buckets or objects in a bucket, optionally constrained by a prefix."""
        brief = options.get('brief', False)
        if not args:
            buckets = self.s3.GetAllBuckets()
            print '\n'.join(
                [brief and b.Name or '%s  %s' % (b.CreationDate.ToString('r'), b.Name) for b in buckets])
        else:
            bucket, prefix = parse_s3uri(args.pop(0))
            objs = self.s3.ListAllObjects(bucket, prefix)
            for obj in objs:
                if type(obj) == CommonPrefix:
                    display = brief and obj.Prefix or ' ' * 53 + obj.Prefix
                else:
                    display = brief and obj.Key[len(prefix):] or '%s  %20s  %s' % (
                        obj.LastModified.ToString('r'), 
                        obj.Size.ToString('N0'),
                        obj.Key[len(prefix):])
                print display

    list.opt_specs = ('brief', )
    list.opt_flags = ('brief', )

    def put(self, args, options):
        """Puts a local file as an object in a bucket."""
        if not args:
            raise Exception('Missing target object path.')
        bucket, key = parse_s3uri(args.pop(0))
        if not args:
            raise Exception('Missing local file path.')
        fpath = args.pop(0)
        if not key or key[-1] == '/':
            key = (key and key or '') + Path.GetFileName(fpath)
        content_type = options.get('content-type', MIME_MAP.get(Path.GetExtension(fpath), 'application/octet-stream'))
        acl = parse_canned_acl_arg(options.get('acl'))
        fname = Path.GetFileName(fpath)
        preamble = 'Uploading %s (%s bytes) as %s...' % (fname, FileInfo(fpath).Length.ToString('N0'), content_type)
        print preamble,
        iswin = is_windows()
        def on_progress(sender, args):
            if iswin:
                print '\r%s %s (%d%%)' % (preamble, args.BytesTransferred.ToString('N0'), args.ProgressPercentage),
        try:
            self.s3.AddObjectProgress += on_progress
            self.s3.AddObject(fpath, bucket, key, content_type, acl)
        finally:
            self.s3.AddObjectProgress -= on_progress
        print 'OK'
    
    put.opt_specs = ('content-type', 'acl')

    def puts(self, args, options):
        """Puts text from standard input as an object in a bucket."""
        if not args:
            raise Exception('Missing target object for text.')
        bucket, key = parse_s3uri(args.pop(0))
        if not key:
            raise Exception('Missing key for text.')
        acl = parse_canned_acl_arg(options.get('acl'))
        txt = sys.stdin.read()
        print 'Uploading %s characters of text...' % len(txt).ToString("N0"),
        self.s3.AddObjectString(txt, bucket, key, 'text/plain', acl)
        print 'OK'

    puts.opt_specs = ('acl', )

    def get(self, args):
        """Gets an object from a bucket as a local file."""
        if not args:
            raise Exception('Missing source object path.')
        bucket, key = parse_s3uri(args.pop(0))
        if not key:
            raise Exception('Missing key.')
        name = key.split('/')[-1]
        fpath = args and args.pop(0) or None
        isdir = Directory.Exists(fpath)
        if not fpath or isdir:
            fpath =  (isdir and fpath + '\\' or '') + name
        preamble = 'Downloading %s to %s...' % (key, Path.GetFileName(fpath))
        print preamble,        
        iswin = is_windows()
        def on_progress(sender, args):
            if iswin:
                print '\r%s %s (%d%%)' % (preamble, args.BytesTransferred.ToString('N0'), args.ProgressPercentage),
        try:
            self.s3.GetObjectProgress += on_progress
            self.s3.GetObject(bucket, key, fpath)
        finally:
            self.s3.GetObjectProgress -= on_progress
        print 'OK'

    def gets(self, args):
        """Sends an object from a bucket to standard output."""
        print self.__gets(args)[-1]

    def pops(self, args):
        """Removes and sends an object from a bucket to standard output."""
        bucket, key, txt = self.__gets(args)
        print txt
        self.rm([Uri(Uri('s3://' + bucket), key).ToString()])

    def rm(self, args):
        """Removes an from a bucket."""
        if not args:
            raise Exception('Missing object path.')
        bucket, key = parse_s3uri(args.pop(0))
        if not key:
            raise Exception('Missing key.')
        self.s3.DeleteObject(bucket, key)

    def authurl(self, args, options):
        """Creates a pre-authorized URI valid for performing a GET."""
        if not args:
            raise Exception('Missing object path.')
        bucket, key = parse_s3uri(args.pop(0))
        if not key:
            raise Exception('Missing key.')
        expires = DateTime.Parse(options.get('expires', DateTime.Now.AddHours(1).ToString()))
        print self.s3.GetAuthorizedUrl(bucket, key, expires)

    authurl.opt_specs = ('expires', )

    def __gets(self, args):
        if not args:
            raise Exception('Missing source object path.')
        bucket, key = parse_s3uri(args.pop(0))
        if not key:
            raise Exception('Missing key.')
        content_type = clr.Reference[str]()
        content_length = clr.Reference[Int64]()
        input = self.s3.GetObjectStream(bucket, key, content_length, content_type)
        try:
            content_length, content_type = content_length.Value, content_type.Value
            if 'text/plain' != content_type:
                raise Exception('Object is %s, not text/plain.' % content_type)
            output = MemoryStream()
            copy_stream(input, output, content_length)
        finally:
            input.Close()
        txt = Encoding.UTF8.GetString(output.GetBuffer(), 0, content_length)
        return (bucket, key, txt)
        
def app_lpath(rhs = None, dont_make = False):
    """Creates a path under where local application data is stored."""
    path = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData), 'LitS3')
    if not dont_make and not Directory.Exists(path):
        Directory.CreateDirectory(path)
    return rhs and Path.Combine(path, rhs) or path

def protect_user_str(secret, entropy):
    """Protects a string for the current user."""
    return ProtectedData.Protect(Encoding.UTF8.GetBytes(secret), entropy, DataProtectionScope.CurrentUser)

def unprotect_user_str(secret, entropy):
    """Unprotects a string previously protected for the current user."""
    return Encoding.UTF8.GetString(ProtectedData.Unprotect(secret, entropy, DataProtectionScope.CurrentUser))

def save_aws_ids(path, id, key):
    """Saves AWS identifiers securely to a file."""
    entropy = Array.CreateInstance(Byte, 16)
    RNGCryptoServiceProvider().GetBytes(entropy)
    id, key = protect_user_str(id, entropy), protect_user_str(key, entropy)
    File.WriteAllText(path, Environment.NewLine.join([Convert.ToBase64String(item) for item in (entropy, id, key)]))

def load_aws_ids(path):
    """Loads AWS identifiers from a secured file."""
    lines = File.ReadAllLines(path)[:3]
    entropy, id, key = [Convert.FromBase64String(line) for line in lines]
    return unprotect_user_str(id, entropy), unprotect_user_str(key, entropy)
       
def print_help(args):
    print """LitS3 Commander - $Revision: 100 $
Command-line interface to LitS3
http://lits3.googlecode.com/
"""
    options, args = parse_options(args, ('version', ), ('version', ))
    
    if options.get('version', False):
        from System import AppDomain
        from System.Diagnostics import DebuggableAttribute
        asm = clr.GetClrType(S3Service).Assembly
        asm_name = asm.GetName()
        print 'Using %s %s from:' % (asm_name.Name, asm_name.Version)
        cb = Uri(asm.CodeBase)
        print cb.IsFile and cb.LocalPath or cb
        print
        print 'Assemblies:'
        print
        print '\n'.join([str(asm) for asm in AppDomain.CurrentDomain.GetAssemblies()])
        return

    print """Usage:

  %(this)s COMMAND ARGS
 
where:

  COMMAND is one of:
    ls (list), put, get, puts, gets, pops, rm (del), 
    authurl, mkbkt, rmbkt, ids, 
    about
  ARGS
    COMMAND-specific arguments
    
All commands require two arguments:

  --aws-key-id VALUE      Your AWS access key ID
  --aws-secret-key VALUE  Your AWS secret access key

The access identifiers can be set into your environment. If you then 
use a dash where an identifier is expected then the corresponding value 
will be picked up from the environment. The environment variables 
sought are AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY. With those in 
place, you can simply resort to the second usage:
 
  %(this)s COMMAND --aws-key-id - --aws-secret-key - ARGS
  
The access identifiers can also be securely saved into a file instead
of environment variables. To do this, use "ids" (without quotes) as
COMMAND. If the access identifiers can be found in the saved file
upon start-up then the corresponding arguments can be dropped.
 
Each COMMAND has its own set of ARGS. Also as a general rule, each 
COMMAND that works with an object uses a simple path scheme to 
identify the object. That scheme simply looks like this:
 
  "s3://" BUCKET ( "/" KEY )
 
Examples:
 
%(this)s ls
  List all my buckets
 
%(this)s ls s3://foo
  List all objects in foo bucket
 
%(this)s ls s3://foo/images/
  List all objects in bucket foo with the common prefix of images/
 
%(this)s put s3://foo index.html
  Add local file named index.html as key index.html in bucket foo
 
%(this)s put s3://foo/images/ ani.gif
  Add local file named ani.gif as key images/ani.gif in bucket foo
 
%(this)s put s3://foo/images/animation.gif ani.gif
  Add local file named ani.gif as key images/animation.gif 
  in bucket foo
 
%(this)s put s3://foo/script script --content-type text/plain
  Add local file named script as key script in bucket foo and
  set its content type to plain text

%(this)s get s3://foo/index.html
  Get object with key index.html in bucket foo as local file named 
  index.html
 
%(this)s get s3://foo/index.html bar.html
  Get object with key index.html in bucket foo as local file 
  named bar.html
 
%(this)s rm s3://foo/index.html
  Remove the object with key index.html in the bucket foo
 
dir | %(this)s puts s3://foo/dir.txt
  Puts the output from dir (on Windows; ls on Unix platforms) as a 
  plain text object named dir.txt in bucket foo
 
%(this)s gets s3://foo/dir.txt
  Gets the plain text object named dir.txt in bucket foo and writes 
  its content to standard output
 
%(this)s pops s3://foo/dir.txt
  Gets the plain text object named dir.txt in bucket foo, writes its 
  content to standard output and then removes the object.

%(this)s authurl s3://foo/bar
  Get a pre-authenticated URL for object with key bar in the 
  bucket foo that expires in an hour

%(this)s authurl s3://foo/bar --expires 2010-01-01
  Get a pre-authenticated URL for object with key bar in the 
  bucket foo that expires on January 1st, 2010

%(this)s mkbkt foo
  Creates a new bucket called foo in U.S.

%(this)s mkbkt foo --europe
  Creates a new bucket called foo in E.U.

%(this)s rmbkt foo
  Delete the bucket called foo if it is empty
""" % { 'this': Path.GetFileNameWithoutExtension(sys.argv[0]) }
        
def main(args):

    if not args:
        raise Exception('Missing command. Try help.')
    
    cmd = args.pop(0)
    if 'help' == cmd:
        print_help(args)
        return

    ids_fpath = GetEnvironmentVariable('AWS_IDS_FILE') or app_lpath('aws-ids')
    saved_id, saved_key = File.Exists(ids_fpath) and load_aws_ids(ids_fpath) or (None, None)

    options, args = lax_parse_options(args, ('aws-key-id', 'aws-secret-key'))

    id = options.get('aws-key-id', '-')
    if id == '-':
        id = GetEnvironmentVariable('AWS_ACCESS_KEY_ID') or saved_id
    if not id:
        raise Exception('Missing AWS access key ID.')

    key = options.get('aws-secret-key', '-')
    if key == '-':
        key = GetEnvironmentVariable('AWS_SECRET_ACCESS_KEY') or saved_key
    if not key:
        raise Exception('Missing AWS secret access key.')

    if 'ids' == cmd:
        ids_fpath = args and args.pop(0) or ids_fpath
        save_aws_ids(ids_fpath, id, key)
        print 'AWS identifiers securely saved to:'
        print Path.GetFullPath(ids_fpath)
        return

    s3 = S3Service(AccessKeyID = id, SecretAccessKey = key)
    S3Commander(s3)(cmd, args)

if __name__ == '__main__':
    try:
        main(sys.argv[1:])
    except Exception, e:
        print >> sys.stderr, e
        sys.exit(1)
