const express = require("express");
const app = express();
const PORT = 8085 || process.env.PORT;

app.use(express.json());

app.listen(PORT, () => console.log(`Server started at port : ${PORT}`));

// Load Routes
const users =  require("./router/api/users");

app.use("/api/v0/users", users);