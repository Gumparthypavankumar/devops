const User = require('../models/User');

const Users = [
    new User(
        1,
        "John",
        "Doe",
        "john@email.com"
    ),
    new User(
        2,
        "Jean",
        "Smith",
        "jean@email.com"
    ),
    new User(
        3,
        "Harry",
        "Smith",
        "harrysmith@email.com"
    )
]; 

module.exports = Users;