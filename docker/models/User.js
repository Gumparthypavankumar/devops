class User{
    constructor(id, firstName, lastName, email){
        this.id = id;
        this.firstName = firstName;
        this.lastName = lastName;
        this.email = email;
        this.isLocked = false;
        this.isBlocked = false;
        this.createdAt = new Date();
        this.updatedAt = new Date();
    }
}

module.exports = User;