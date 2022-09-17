const app = require("express");
const router = app.Router();
const { getUsers, findById, createUser, updateUser } = require('../../actions/Users');
const { SuccessResponse, ErrorResponse } = require("../../models/ApiResponse");

router.get('', function(req, res){
    const users = getUsers();
    return res.status(200).json(
        new SuccessResponse()
            .setData(users)
            .setMessage("Users fetched Successfully")
    );
});

router.get('/:id', function(req, res){
    const userId = parseInt(req.params.id);
    const user = findById(userId);
    if(!user) {
        return res.status(400).json(
            new ErrorResponse()
                .setErrors([])
                .setErrMess(`User with ${userId} does not exist`)
                .setErrCode(101)
        );
    } 
    return res.status(200).json(
        new SuccessResponse()
            .setData(user)
            .setMessage(`SuccessFully fetched user with id ${userId}`)
        );
});

router.post('', function(req, res){
    const { firstName, lastName, email } = req.body;
    const users = createUser(firstName, lastName, email);
    return res.status(201).json(
        new SuccessResponse()
        .setData(users)
        .setMessage('User Created Successfully')
    );
});

router.put('/:id', function(req, res){
    const userId = parseInt(req.params.id);
    const { firstName, lastName, email, isLocked, isBlocked } = req.body;
    try{
        const user = updateUser(userId, {firstName, lastName, email, isLocked, isBlocked});
        return res.status(200).json(
            new SuccessResponse()
            .setData(user)
            .setMessage('User Updated Successfully')
        );
    }catch(err){
        if(!(err.name === 'ClientError')) {
            return res.status(500).json(
                new ErrorResponse()
                    .setErrors([])
                    .setErrMess(err.message)
                    .setErrCode(500)
            ); 
        }
        return res.status(400).json(
            new ErrorResponse()
                .setErrors([])
                .setErrMess(err.message)
                .setErrCode(err.code)
        );
    }
});

module.exports = router;