import upload from "./upload.middleware.js";

router.post(

    "/",

    upload.single("image"),

    Controller.create

);