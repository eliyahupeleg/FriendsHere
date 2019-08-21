# -*- coding: utf-8 -*-
import sql


class User(object):

    # creating new friends.
    def __init__(self, id, gender, x_cor, y_cor, name, age, birthday, phone, last_seen, in_database):

        # set the data of the user.
        self.id = id
        self.gender = gender
        self.x_cor, self.y_cor = x_cor, y_cor
        self.name = name
        self.age = age
        self.birthday = birthday
        self.phone = phone
        self.last_seen = last_seen

        # "U" for user (the first char in the class name) or "S" for SuperUser
        self.type = str(type(self).__name__)[0:1:1]

        # cant use the "set" functions- not defined yet. all the function getting there data from the database-
        # even if the server is off or crashed, everything saved.

        # if the user exist..
        if in_database:

            # recover the data from the database.

            self.gender = str(sql.select("Users", "gender", "id", self.id))[3:-3:]
            self.x_cor, self.y_cor = str(sql.select("Users", "x_cor", "id", self.id))[3:-3:], str(
                sql.select("Users", "y_cor", "id", self.id))[3:-3:]
            self.name = str(sql.select("Users", "name", "id", self.id))[3:-3:]
            self.age = str(sql.select("Users", "age", "id", self.id))[3:-3:]
            self.last_seen = str(sql.select("Users", "last_seen", "id", self.id))[3:-3:]
            self.type = str(sql.select("Users", "type", "id", self.id))[3:-3:]
            self.birthday = str(sql.select("Users", "birthday", 'id', self.id))[3:-3:]
            self.phone = str(sql.select("Users", "phone", 'id', self.id))[3:-3:]

        else:
            # create new user with this parameters.
            sql.insert("Users",
                       ("id", "gender", "x_cor", "y_cor", "name", "age", "last_seen", "type", "phone", "birthday"),
                       (self.id, self.gender, self.x_cor, self.y_cor, self.name, self.age, self.last_seen, self.type,
                        self.phone, self.birthday))

    # all the "get" functions getting there data from the database- even if the server crashed, the data is safe.
    def get_id(self):
        return self.id

    # not using  2 functions for (cor_x, cor_y) because they are requesting always together.
    def get_location(self):
        return float(str(sql.select("Users", "x_cor", "id", self.id))[3:-3:]), \
               float(str(sql.select("Users", "y_cor", "id", self.id))[3:-3:])

    def get_gender(self):
        return str(sql.select("Users", "gender", "id", self.id))[3:-3:]

    def get_type(self):
        return str(sql.select("Users", "type", "id", self.id))[3:-3:]

    def get_age(self):
        return str(sql.select("Users", "age", "id", self.id))[3:-3:]

    def get_last_seen(self):
        return str(sql.select("Users", "last_seen", "id", self.id))[3:-3:]

    def get_phone(self):
        return str(sql.select("Users", "phone", "id", self.id))[3:-3:]

    def get_birthday(self):
        return str(sql.select("Users", "birthday", "id", self.id))[3:-3:]

    def get_radius(self):
        return 1

    # the all set function using the database- beckup, even when the server crashing or closing.

    # not using  2 functions for (cor_x, cor_y) because they will change always together.
    def set_location(self, new_x_cor, new_y_cor):
        sql.update("Users", ("x_cor", "y_cor"), (new_x_cor, new_y_cor), "id = '" + self.id + "'")
        self.x_cor, self.y_cor = new_x_cor, new_y_cor

    def set_last_seen(self, new_last_seen):
        sql.update("Users", ("last_seen",), (new_last_seen,), "id = '" + self.id + "'")
        self.last_seen = new_last_seen

    def set_id(self, new_id):
        sql.update("Users", ("id",), (new_id,), "id = '" + self.id + "'")
        self.id = new_id

    def set_phone(self, new_phone):
        sql.update("Users", ("age",), (new_phone,), "id = '" + self.id + "'")
        self.phone = new_phone

    # print the all data in the best way.
    def __repr__(self):
        return "name : {}. id : {}. age : {}. gander : {}. location x, y: {}, {}. last seen : {}, invited_by: {}".format(
            self.name, self.id, self.age, self.gender, self.x_cor, self.y_cor, self.last_seen, self.invited_by)


class SuperUser(User):
    def __init__(self, id, gender, loc_x, loc_y, name, age, birthday, phone, last_seen, in_database, invited_by,
                 friends_radius):
        super(SuperUser, self).__init__(id, gender, loc_x, loc_y, name, age, birthday, phone, last_seen, in_database)

        self.invitations = "0"
        self.friends_radius = friends_radius
        self.invited_by = invited_by

        if in_database:
            self.friends_radius = str(sql.select("Users", "friends_radius", "id", self.id))[3:-3:]
            self.invitations = str(sql.select("Users", "invitations", "id", self.id))[3:-3:]
            self.invited_by = str(sql.select("Users", "phone", 'invited_by', self.id))[3:-3:]
        else:
            sql.update("Users", ("friends_radius", "invitations", "invited_by"),
                       (self.friends_radius, self.invitations, self.invited_by),
                       "id = '" + self.id + "'")

    def set_radius(self, new_radius):
        sql.update("Users", ("friends_radius",), (new_radius,), "id = '" + self.id + "'")
        self.friends_radius = new_radius

    def set_invitations(self, new_invitations):
        sql.update("Users", ("invitations",), (new_invitations,), "id = '" + self.id + "'")
        self.invitations = new_invitations

    def get_radius(self):
        return str(sql.select("Users", "friends_radius", "id", self.id))[3:-3:]

    def get_invited_by(self):
        return str(sql.select("Users", "invited_by", "id", self.id))[3:-3:]

    def get_invitations(self):
        return str(sql.select("Users", "friends_radius", "id", self.id))[3:-3:]

    def __repr__(self):
        return "name : {}. id : {}. age : {}. gander : {}. location x, y: {}, {}. last seen : {}, invited_by: {}," \
               " invitations: {}".format(
            self.name, self.id, self.age, self.gender, self.x_cor, self.y_cor, self.last_seen, self.invited_by,
            self.invitations)
