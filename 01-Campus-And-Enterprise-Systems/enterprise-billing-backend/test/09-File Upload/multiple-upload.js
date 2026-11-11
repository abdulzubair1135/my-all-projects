import upload from "./upload.middleware.js";

router.post(

    "/",

    upload.array(

        "images",

        5

    ),

    Controller.create

);