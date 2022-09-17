const users = require("../data");
const User = require('../models/User');
const { ClientError } = require('../Errors');

function getUsers(){
    return users;
}

function findById(userId){
    userId = parseInt(userId);
    return users.find(user => user.id === userId);
}

function createUser(firstName, lastName, email){
    const user = new User(
        users.length + 1,
        firstName,
        lastName, 
        email
    );
    users.push(user);
    return users;
}

function updateUser(userId, {firstName, lastName, email, isLocked, isBlocked}){
    const user = users.find(user => user.id === userId);
    if(!user) throw new ClientError(`User with id: ${userId} does not exist`, 400);
    user.firstName = firstName;
    user.lastName = lastName;
    user.email = email;
    user.isLocked = isLocked;
    user.isBlocked = isBlocked;
    user.updatedAt = new Date();
    return user;
}

module.exports = {
    getUsers,
    findById,
    createUser,
    updateUser
}