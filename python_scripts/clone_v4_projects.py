# Python 2.7
#  Clone all projects from a old GitLab server (V4 API)
import os
import sys
import shutil
import json
import urllib2, ssl
import getopt

gConfig = {"apiToken":"", "server":"", "httpUsername":"", "actualRun":False, "outputDir":"clone_v4"}

############################################################################
# Command line arguments
############################################################################
def ShowHelp():
    print ("python %s [OPTIONS] OUTPUT_DIR" % sys.argv[0])
    print ("    -t TOKEN, --token=TOKEN             Set API token")
    print ("    -s SERVER, --server=SERVER          Set server address")
    print ("    -u USERNAME, --user=USERNAME        Set HTTPS username")
    print ("    -a, --actualRun                     Without this, the clone action will skip.")
    print ("    -h, --help                          Show this help.")
    print (" ")
    print ("Example: python %s -t 123456 -h git.host.com:8080 -u admin -a" % sys.argv[0])

def GetArguments():
    try:
        opts, args = getopt.getopt(sys.argv[1:],"aht:s:u:",["token=","server=","user="])
    except getopt.GetoptError:
        ShowHelp ()
        sys.exit(1)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            ShowHelp ()
            sys.exit(0)
        elif opt in ("-t", "--token"):
            gConfig["apiToken"] = arg
            print ("apiToken=%s" % arg)
        elif opt in ("-s", "--server"):
            gConfig["server"] = arg
            print ("server=%s" % arg)
        elif opt in ("-u", "--user"):
            gConfig["httpUsername"] = arg
        elif opt in ("-a", "--actualRun"):
            gConfig["actualRun"] = True
    if args and args[0] != '-':
        gConfig["outputDir"] = args[0]
    # Check all variable set
    for key in gConfig.keys():
        if (gConfig[key] == ""):
            print ("!!%s not set" % key)
            ShowHelp ()
            sys.exit(1)

    return gConfig

############################################################################
############################################################################
def GetProjectListHeader(aItem):
    try:
        url = "https://" + gConfig["server"] + "/api/v4/projects"
        ctx = ssl._create_unverified_context()
        req = urllib2.Request(url)
        req.add_header ("PRIVATE-TOKEN", gConfig["apiToken"])
        response = urllib2.urlopen(req, context=ctx)
        return int (response.info ()[aItem])
    except urllib2.URLError as error:
        print error.reason
    except ValueError:
        print("JSON parse error.")
    except:
        print("Unexpected error:", sys.exc_info()[0])
    return -1

############################################################################
############################################################################
def GetProjectPage(aPage):
    try:
        url = "https://" + gConfig["server"] + "/api/v4/projects" + "?page=" + str(aPage)
        print ("URL: %s" % url)
        ctx = ssl._create_unverified_context()
        req = urllib2.Request(url)
        req.add_header ("PRIVATE-TOKEN", gConfig["apiToken"])
        response = urllib2.urlopen(req, context=ctx)
        html = response.read()
        j_obj = json.loads(html)
        return j_obj
    except urllib2.URLError as error:
        print error.reason
    except ValueError:
        print("JSON parse error.")
    except:
        print("Unexpected error:", sys.exc_info()[0])
    return None

############################################################################
############################################################################
def GetProjectList ():
    # Get number of pages
    num_of_pages = GetProjectListHeader("X-Total-Pages")
    if (num_of_pages < 0):
        return None
    print ("Number of pages=%d" % num_of_pages)

    # Get all page and append together
    j_project_list = json.loads ("[]")
    for page in range (1, num_of_pages + 1):
        j_obj = GetProjectPage(page)
        if (j_obj is None):
            return None
        for x in j_obj:
            j_project_list.append(x)

    return j_project_list

############################################################################
############################################################################
def SaveProjectList (aTargetFile, j_project_list):
    try:
        with open(aTargetFile, 'w') as f:
            json.dump (j_project_list, f, indent=2)
            f.write ("\n")
            f.close ()
            return True
    except IOError as e:
        print "I/O error({0}): {1}".format(e.errno, e.strerror)
    except:
        print("Unexpected error:", sys.exc_info()[0])
    return False


############################################################################
# Start
############################################################################
gConfig = GetArguments()

# Remove output directory
print ("Output directory: %s" % gConfig["outputDir"])
try:
    if (os.path.isdir (gConfig["outputDir"])):
        shutil.rmtree (gConfig["outputDir"])
        print("Directory %s removed." % gConfig["outputDir"])
    elif (os.path.isfile (gConfig["outputDir"])):
        os.remove (gConfig["outputDir"])
        print("File %s removed." % gConfig["outputDir"])
    os.mkdir (gConfig["outputDir"])
except OSError as error: 
    print(error) 
    sys.exit (1)

# Get projects
j_project_list = GetProjectList ()
if (j_project_list is None):
    sys.exit (1)

num_of_project = len ([prj for prj in j_project_list])
print ("%d projects found." % num_of_project)

# Save project list
list_file = gConfig["outputDir"] + "/list.json"
print ("Project List file: %s" % list_file)
if (not SaveProjectList (list_file, j_project_list)):
    sys.exit (1)

# Process each project
for x in j_project_list:
    ssh_url = x["ssh_url_to_repo"]
    http_url = x["http_url_to_repo"]
    namespace_path = gConfig["outputDir"] + "/" + x["namespace"]["path"]
    path = gConfig["outputDir"] + "/" + x["path_with_namespace"]
    try: 
        if (not os.path.exists (namespace_path)):
            os.makedirs (namespace_path)
        cmd = "cd " + namespace_path
        cmd += " && env GIT_SSL_NO_VERIFY=true git clone --mirror " + http_url.replace ("https://", "https://" + gConfig["httpUsername"] + ":" + gConfig["apiToken"] + "@")
        print (cmd)
        if (gConfig["actualRun"]):
            if (os.system (cmd)):
                print ("Command error!")
                sys.exit(1)
        else:
            print ("!Clone skipped.")
    except OSError as error: 
        print(error) 
        sys.exit (1)

#
print ("All Done.")
