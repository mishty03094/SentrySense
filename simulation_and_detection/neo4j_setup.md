Neo4j Setup on macOS with Homebrew
1. Install Neo4j
Open your terminal and run:

bash
brew install neo4j
This will download and install the latest stable Neo4j Community Edition on your Mac.

2. Start Neo4j
You have two ways to start Neo4j:

A. As a background service (recommended):
bash
brew services start neo4j
This will start Neo4j and make it run automatically after reboot.

B. In the terminal (foreground/console mode):
bash
neo4j console
or (if installed in a specific path):

bash
/opt/homebrew/opt/neo4j/bin/neo4j console
This will keep Neo4j running in your terminal window. To stop, press Ctrl+C.

3. Access the Neo4j Browser
Open your web browser and go to:
http://localhost:7474/browser/

The default username and password are both:

text
neo4j
On your first login, you will be prompted to set a new password.

4. Common Commands
Check status:


neo4j status
Stop Neo4j:


brew services stop neo4j
or


neo4j stop
Restart Neo4j:



Browser UI	http://localhost:7474/browser/
 

 WINDOWS

Neo4j Setup on Windows (Terminal/Command Prompt)
1. Download Neo4j
Go to the Neo4j Download Center.

Download the Community Edition Windows zip/exe installer7.

2. Install Neo4j
If you downloaded an installer (.exe), run it and follow the prompts.

If you downloaded a zip file:

Extract it to a folder, e.g., C:\neo4j.

Open Command Prompt (cmd) and navigate to the extracted folder:

text
cd C:\neo4j
3. (Optional) Set JAVA_HOME
Neo4j needs Java (JDK 17+). Make sure Java is installed and the JAVA_HOME environment variable is set.

To check Java:

text
java -version
If not installed, download from Oracle.

Add Java's bin directory to your PATH if needed9.

4. Start Neo4j
You can start Neo4j in two ways:

A. As a Console Application (Recommended for Dev)
text
bin\neo4j console
This opens Neo4j in the terminal and shows logs.

To stop, press Ctrl+C.

B. As a Windows Service (Runs in Background)
text
bin\neo4j windows-service install
bin\neo4j start
To stop the service:

text
bin\neo4j stop
To uninstall the service:

text
bin\neo4j windows-service uninstall
5. Access Neo4j Browser
Open your browser and go to:
http://localhost:7474

Default username: neo4j

Default password: neo4j (you’ll be prompted to set a new password on first login)69.


