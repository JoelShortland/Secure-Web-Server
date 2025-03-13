This project was originally part of an ISYS2120 project at USYD. It uses a mix of Python, SQL and Javascript to allow for secure communication between a webpage and server. Primarily exists as a way to demonstrate knowledge of cybersecurity including hashing and the https protocol.  

The project is used to set up an e2ee communication tool on web.
To run:
1. Do not use IE to visit the web app.
2. Make sure you python version is 3.7 or newer one
3. Do not require any third party libraries 
4. When first to run the program, run "python3 run.py reset_db" first
5. Then run "python3 run.py"
6. Then visit https://127.0.0.1 
7. Then register two Usrs whose uname is "12345" and "123456"( Hint: After you register, you do not log in automatically)
8. According to the friend list is hard coded, if you register as other users, you can not be sent message
9. After you log in, go to message page, click the user you plan sent the message to, type in messages and click submit.
10. You are allowed to send message to yourself for test issues.
11. If you do not see the message, refresh the page.(auto request once per second is a disaster for testing and debug)
12. One browser only allow one user to log in at the same time(You can log in as 12345 on Edge and 123456 on Chrome)
13. We do not have a log out button. If you wish to log out, restart the server or manually clear all cookies on browser.
