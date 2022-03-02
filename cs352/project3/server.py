import socket
import signal
import sys
import random

# Read a command line argument for the port where the server
# must run.
port = 8080
if len(sys.argv) > 1:
    port = int(sys.argv[1])
else:
    print("Using default port 8080")

# Start a listening server socket on the port
sock = socket.socket()
sock.bind(('', port))
sock.listen(2)

### Contents of pages we will serve.
# Login form
login_form = """
   <form action = "http://localhost:%d" method = "post">
   Name: <input type = "text" name = "username">  <br/>
   Password: <input type = "text" name = "password" /> <br/>
   <input type = "submit" value = "Submit" />
   </form>
""" % port
# Default: Login page.
login_page = "<h1>Please login</h1>" + login_form
# Error page for bad credentials
bad_creds_page = "<h1>Bad user/pass! Try again</h1>" + login_form
# Successful logout
logout_page = "<h1>Logged out successfully</h1>" + login_form
# A part of the page that will be displayed after successful
# login or the presentation of a valid cookie
success_page = """
   <h1>Welcome!</h1>
   <form action="http://localhost:%d" method = "post">
   <input type = "hidden" name = "action" value = "logout" />
   <input type = "submit" value = "Click here to logout" />
   </form>
   <br/><br/>
   <h1>Your secret data is here:</h1>
""" % port

#### Helper functions
# Printing.
def print_value(tag, value):
    print("Here is the", tag)
    print("\"\"\"")
    print(value)
    print("\"\"\"")
    print()

# Signal handler for graceful exit
def sigint_handler(sig, frame):
    print('Finishing up by closing listening socket...')
    sock.close()
    sys.exit(0)
# Register the signal handler
signal.signal(signal.SIGINT, sigint_handler)


# TODO: put your application logic here!
# Read login credentials for all the users
# Read secret data of all the users

# Password database {key: (pw, secret)}
data = dict()
pwFile = open("passwords.txt", 'r')
secretsFile = open("secrets.txt", 'r')
pwFile = pwFile.read().splitlines()
secretsFile = secretsFile.read().splitlines()

for line in pwFile:
    splitLine = line.split()
    data[splitLine[0]] = (splitLine[1],)

for line in secretsFile:
    splitLine = line.split()
    data[splitLine[0]] = (data[splitLine[0]][0], splitLine[1])

### Loop to accept incoming HTTP connections and respond.
while True:
    client, addr = sock.accept()
    req = client.recv(1024)

    # Let's pick the headers and entity body apart
    header_body = req.split('\r\n\r\n')
    headers = header_body[0]
    body = '' if len(header_body) == 1 else header_body[1]
    print_value('headers', headers)
    print_value('entity body', body)

    # TODO: Put your application logic here!
    # Parse headers and body and perform various actions
    # body = "username=bezos&password=amazon"
    # body = "username=bezos"

    username = password = action = None
    body = body.split('&') if body != '' else []
    print('body', body)
    for field in body:
        param = field.split('=')
        if param[0] == 'username':
            username = param[1]
        elif param[0] == 'password':
            password = param[1]
        elif param[0] == 'action':
            action = 'logout'

    if username == None and password == None:  # Default login
        html_content_to_send = login_page 
    elif username in data and data[username][0] == password: # Good login
        html_content_to_send = success_page + data[username][1]  # success page + secret
    elif username is None or password is None or username not in data or password != data[username][0]: # empty or incorrect fields
        html_content_to_send = bad_creds_page # Retry login
    elif action == 'logout':
        html_content_to_send = logout_page
    else: # Default login, should never get here
        html_content_to_send = login_page 


    # You need to set the variables:
    # (1) `html_content_to_send` => add the HTML content you'd
    # like to send to the client.
    # Right now, we just send the default login page.
    # html_content_to_send = login_page
    # But other possibilities exist, including

    # html_content_to_send = bad_creds_page
    # html_content_to_send = logout_page
    
    # (2) `headers_to_send` => add any additional headers
    # you'd like to send the client?
    # Right now, we don't send any extra headers.
    headers_to_send = ''

    # Construct and send the final response
    response  = 'HTTP/1.1 200 OK\r\n'
    response += headers_to_send
    response += 'Content-Type: text/html\r\n\r\n'
    response += html_content_to_send
    print_value('response', response)    
    client.send(response)
    client.close()
    
    print("Served one request/connection!")
    print()

# We will never actually get here.
# Close the listening socket
sock.close()
