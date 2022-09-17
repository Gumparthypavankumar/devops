class SuccessResponse{
    constructor(){
        this.message = "";
        this.data = null;
    }

    setData(data){
        this.data = data;
        return this;
    }

    setMessage(message){
        this.message = message;
        return this;
    }
}

class ErrorResponse{
    constructor(){
        this.errors = [];
        this.errorMess = null;
        this.errorCode = null;
    }

    setErrors(errors){
        this.errors = errors;
        return this;
    }

    setErrMess(errorMess){
        this.errorMess = errorMess;
        return this;
    }

    setErrCode(errorCode){
        this.errorCode = errorCode;
        return this;
    }
}

module.exports = {
    SuccessResponse,
    ErrorResponse
};