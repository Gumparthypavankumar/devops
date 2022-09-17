class ClientError extends Error{
    constructor(message, code){
        super(message);
        this.name = 'ClientError';
        this.code = code;
    }
}

module.exports = {
    ClientError
};