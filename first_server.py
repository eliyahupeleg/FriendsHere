# -*- coding: utf-8 -*-
import socket
import datetime
import sql
import classes
import geopy.distance
import threading

# the server connection data.
HOST = "0.0.0.0"
PORT = 8820

# list of the users. every user will be call: my_user[user_id].
# easy way to call the users from the list without another id.
my_users = {}


# finding the user contacts that using the app too.
def find_friends(user_id):
    # if the contact using the app, the "friend_id" will save his id.
    # else, the "friend_id" will be NULL.
    selected = sql.select("friends", "friend_id", "friend_id IS NOT NULL AND id ", user_id)

    if selected:
        for i in range(0, len(selected), ):
            # removing the "[""]" from the list.
            selected[i] = str(selected[i])[2:-2:]

        return selected
    return


# returning the friends that in the friends list (parameter),
# and they distance from the user (parameter) is less then the radius that defined to this user.
def friends_here(user_id, friends):
    # will save the friends that they distance from the user is less then the radius that defined for this user.
    active_friends = []

    # saving the location of the user.
    user_loc = my_users[user_id].get_location()

    # if there are some friends to check..
    if friends:

        # run for all the friends.
        for friend in friends:

            # get the friend location, into "friend_loc"
            friend_loc_x = float(str(sql.select("Users", "x_cor", "id", friend))[3:-3:])
            friend_loc_y = float(str(sql.select("Users", "y_cor", "id", friend))[3:-3:])
            friend_loc = friend_loc_x, friend_loc_y

            # id the distance from the user is less then the radius of the user..
            if geopy.distance.distance(user_loc, friend_loc).kilometers <= int(
                    my_users[user_id].get_radius()):
                # add the friend to the active_friends list.
                active_friends.append(friend)

    # if there is at less one friend around..
    if active_friends:

        # return the list.
        return active_friends

    # if not, not using empty list- inviting errors.
    else:
        return ["'"]


# returning the correct time
def get_correct_time():
    # get the correct time into the str "time"
    time = str(datetime.datetime.now())

    # leaves only the digits from "time"
    time = time[0:4] + time[5:7] + time[8:10] + time[11:13] + time[14:16] + time[17:19]

    # time time is the hour, minutes and the second
    time_time = time[8:14]

    # date time is the day, month and year
    time_date = time[:8]

    # changing the format to DD/MM/YY
    time_date = time_date[:4] + time_date[4:6] + time_date[6:8]

    # return the date first, for you can do subtraction between "some time" - "other time" and get the remainder
    return time_date + time_time


# update the last seen of user, to the correct time.
def update_last_seen(user_id):
    my_users[user_id].set_last_seen(get_correct_time())


# update the location of user, to the one in the parameters,
def update_location(user_id, location):
    # slice the location to x and y
    location = str(location[10:-1:])
    x_y = location.split(',')
    x_cor = x_y[0]
    y_cor = x_y[1]

    # "0.0" is an error in the client side.
    if x_cor != "0.0" and y_cor != "0.0":
        # update the location of the user.
        my_users[user_id].set_location(x_cor, y_cor)


# update the contacts of some user.
def update_contacts(user_id, user_contacts_sorted, phone):
    # run on all the contacts.
    for contact in user_contacts_sorted[:-1]:

        # in "contact" got: "name.phone.id".
        contact_id = contact.split(".")[2]
        contact_phone = contact.split(".")[1]
        contact_name = contact.split(".")[0]

        # if the number starting with "+972".
        if contact_phone[0] == "+":
            # change the "+972" to "0".
            contact_phone = "0" + contact_phone[4::]

        # if the name is not regular name, remove the special chars.
        for i in contact_name:
            if i not in "1234567890 abcdefghijklmnopqrstuvwxyz ABCDEFGHIJKLMNOPQRSTUVWXYZ אבגדהוזחטיכלמנסעפצקרשתםןץףך":
                contact_name = contact_name.replace(i, "")

        # if the phone is not regular phone, remove the special chars.
        for i in contact_phone:
            if i not in "1234567890":
                contact_phone = contact_phone.replace(i, "")

        # if the contact not ecist yet..
        if not sql.select("friends", "*", 'id', user_id) or not sql.select("friends", "*", 'friend_phone',
                                                                           contact_phone):
            # create the contact.
            sql.insert("friends", ('id', 'friend_phone', 'friend_name', 'contact_id'),
                       (user_id, contact_phone, contact_name, contact_id))

        # if the contact exist in the users table..
        if sql.select("Users", "id", "phone", contact_phone):
            # update for both of them that there is a friends that
            sql.update("friends", ("friend_id",),
                       (str(sql.select("Users", "id", "phone", contact_phone))[3:-3],),
                       "id= '" + user_id + "' and friend_phone = '" + contact_phone + "'")

            sql.update("friends", ("friend_id",), (user_id,),
                       "id= '" + str(
                           sql.select("Users", "id", "phone", contact_phone)[3:-3:]) + "' and friend_phone = '" +
                       phone + "'")


# create new user.
def create_user(user_id, client_socket):
    # get the age, the gender and the contacts from client.
    user_data = get(client_socket)

    # split the data from the user.
    user_data_list = user_data.split(",")
    print(user_data_list)
    name = user_data_list[0]
    gender = user_data_list[1]
    phone = user_data_list[2]
    birthday = user_data_list[3]
    user_type = user_data_list[4]
    invited_by = user_data_list[5]
    friends_radius = user_data_list[6]
    user_contacts = user_data_list[7]

    # the contacts is like: "contact;contact;"
    user_contacts_sorted = user_contacts.split(";")

    # updating the contacts to the database.
    update_contacts(user_id, user_contacts_sorted, phone)

    print("sending 1")
    # reporting to the client that got all the data.
    send("1", client_socket)

    # cutting the birthday every "." and saving into a list.
    # using because the month or the day can be 2 digit or 1 digit ("1.1.1987", "10.12.2014").
    # so the client adding "." between the day, month and the year.
    age = 2019 - int(birthday.split(".")[2]) - 1

    if user_type == "U":
        # create new user with the permanent parameters.
        my_users[user_id] = classes.User(user_id, gender, "0.0", "0.0", name, age, birthday, phone, get_correct_time(),
                                         False)

    elif user_type == "S":
        # create new SuperUser with the permanent parameters.
        my_users[user_id] = classes.SuperUser(user_id, gender, "0.0", "0.0", name, age, birthday, phone,
                                              get_correct_time(), False, invited_by, friends_radius)


# return true if there is a user with this ID. false if not.
def in_table(user_id):
    # try to get the id from the table Users.
    user_data = sql.select("Users", "*", "id", user_id)

    # if the list is empty, the user not found, then return false. else (the user founded)- return true.
    if not user_data:
        return False
    return True


# checking the id status.
def if_exist_id(user_id):
    # if the is is wrong..
    if not user_id.isdigit():
        # report.
        return "ERROR"

    # if the user unable the permission for getting the id, the function "get_id" will return 0.
    if str(user_id) != "0":

        # check if the user already set in Users database
        if in_table(user_id):
            # return the type of the user- "U" for user and "S" for SuperUser. slicing to remove the list chars ("['']")
            return str(sql.select("Users", "type", "id", user_id))[3:-3:]

        # if the id is correct but not found in users or SuperUsers, return "Not found" = N
        return "N"

    # if the id is incorrect ("0")- return "F" = False
    return "F"


# create the server.
def create_server(host, port):
    # create new server with the PORT and the IP in: HOST, PORT
    server_socket = socket.socket()

    # freeing up the port after using.
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((host, port))

    return server_socket


# connect to the user.
def connect_to_client(server_socket):
    # waite for client/s. max 999,999,999 in the line.
    server_socket.listen(999999999)

    # def client socket and client address, and accept the connection
    (client_socket, client_address) = server_socket.accept()

    return client_socket, client_address


# send str to the user.
def send(message, client_socket):
    client_socket.send(message.encode())


# get str from the user.
def get(client_socket):
    print("getting")
    data = b""

    new = client_socket.recv(1024)
    data += new

    while len(new) == 1024:
        new = client_socket.recv(1024)
        data += new

        print("data:" + str(data))
        print("new" + str(new))
        print("len:" + str(len(new)))

    return str(data.decode())


# create new "user" object by the id and the data from the database.
def restore_user(user_id, user_type):
    # create the object by his type, with his data (recovering from database).
    if user_type == "U":
        my_users[user_id] = classes.User(user_id, None, None, None, None, None, None, True)

    elif user_type == "S":
        my_users[user_id] = classes.SuperUser(user_id, None, None, None, None, None, None, None,
                                              None, True, None, None)


# starting the connecting with user, and send him to new thread.
def start_user_thread(client_socket):
    # for the first "while".
    user_state = "F"

    # run until getting correct id.
    # F = False = incorrect id ("0")
    while user_state == "F" or user_state == "ERROR":

        # get the id from the android device.
        user_id = get(client_socket)

        print(user_id)

        # saving the state of the user.
        user_state = if_exist_id(user_id)

        print(user_state)

        # N = correct ID, but not in any table.
        if user_state == "N":

            # send to user- you are'nt in "Users" table.
            send("0", client_socket)  # not founded id

            # starts new user.
            create_user(user_id, client_socket)
            break

        # if client is "User"..
        elif user_state == "U":

            # send to client- you are a "User" .
            send("U", client_socket)

            # create the user object.
            restore_user(user_id, "U")

            break

        # if client is "SuperUsers"
        elif user_state == "S":

            # send to client- you are a "SuperUsers".
            send("S", client_socket)

            # create new SuperUser object.
            restore_user(user_id, "S")

            break

        else:
            send("error", client_socket)

    if user_state != "N":
        # send to the user his last location. shorter time then starting gps.
        x, y = my_users[user_id].get_location()

        print(str("F," + str(x) + "," + str(y) + "," + my_users[user_id].get_radius()))
        send(str("F," + str(x) + "," + str(y) + "," + my_users[user_id].get_radius()), client_socket)

    # create new thread that will do the updates with the server.
    threading.Thread(target=updates, args=(client_socket, user_id)).start()


# creating the list to send the user.
def list_of_friends_data(friends_around):
    friends_to_send = ""

    for friend in friends_around:
        # save the user data into the list.
        contact_id = str(sql.select("friends", "contact_id", "friend_id", friend))[3:-3:]
        x = str(sql.select("Users", "x_cor", "id", friend))[3:-3:]
        y = str(sql.select("Users", "y_cor", "id", friend))[3:-3:]
        friends_to_send = friends_to_send + x + "'" + y + "'" + contact_id + ";"

    # return the list.
    return friends_to_send


# thread for the updates.
def updates(client_socket, user_id):

    # update all the time.
    while client_socket:

        # get the location from the user.
        loc = get(client_socket)

        print("data update:" + loc)
        # set the radius to the correct one.
        my_users[user_id].set_radius(loc.split(";")[1])

        # split the data from the user.
        loc = loc.split(";")[0]

        # update the user last seen.
        update_last_seen(user_id)

        # update the user location.
        update_location(user_id, loc)

        # find the friends that is around the user.
        friends_around = friends_here(user_id, find_friends(user_id))

        # if there are at less one friend..
        if friends_around != ["'"]:

            # create list of data to the client from the ids of the friends.
            friends_data = list_of_friends_data(friends_around)

        # else..
        else:
            # remove the "[]"
            friends_data = "'"

        # send the new data to the user.
        send(friends_data, client_socket)


def main():
    # create new server with the PORT and the IP in: HOST, PORT
    server_socket = create_server(HOST, PORT)

    # getting users and creating new thread for them.
    while True:
        # def client socket and client address, and accept the connection
        client_socket, client_address = connect_to_client(server_socket)
        threading.Thread(target=start_user_thread, args=(client_socket,)).start()


try:
    # check if the file running by himself and if he is, run the main()
    if __name__ == '__main__':
        main()

except Exception as e:
    print(e)
    input("Enter to exit\n")
    exit()
