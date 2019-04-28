
VERSION = '1.0'

print("Welcome to Graph Client version %s" % VERSION)
print("This repository is used as a tool for a Bachelor Thesis in graph topologies.")
print()
print("Authors for this project are")
print("Oskar Hahr (ohahr@kth.se)")
print("Johan Niklasson (jnikl@kth.se)")
print()

print()
print("Step 1/3")
client_name = ""
while len(client_name) == 0:
    client_name = input("Please enter a client name: ")

print()
print("Step 2/3")
base_url = ""
while len(base_url) == 0:
    print("Enter the base URL to the server pool: ")
    base_url = input()

print()
print("Step 3/3")
thread_count = ""
while not thread_count.replace('0', '').isdigit():
    thread_count = input("Choose a default thread count (the number \r\nof processes that will run simultaneously): ")

f = open(".env", "w+")
f.write("VERSION=%s\r\n" % VERSION)
f.write("CLIENT_NAME=%s\r\n" % client_name)
f.write("BASE_URL=%s\r\n" % base_url)
f.write("THREAD_COUNT=%s\r\n" % thread_count)
f.close()


print()
print("Settings saved")
print("You can now run 'python main.py' to start generating graphs")
