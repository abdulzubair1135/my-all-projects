import jwt from "jsonwebtoken";

const auth = (req, res, next) => {

    const header = req.headers.authorization;

    if (!header) {

        return res.status(401).json({
            success: false,
            message: "No Token"
        });

    }

    const token = header.split(" ")[1];

    console.log("===========");
    console.log("HEADER:", header);
    console.log("TOKEN :", token);
    console.log("SECRET:", process.env.JWT_SECRET);
    console.log("===========");
    try {
        
        req.user = jwt.verify(token, process.env.JWT_SECRET);

        next();

    } catch (err) {

        console.log(err);

        return res.status(401).json({
            success: false,
            message: "Invalid Token"
        });

    }

};

export default auth;