// ======================================================
//
// Admin Access Middleware
//
// ======================================================

const admin = (req, res, next) => {

    if (req.user.role !== "admin") {

        return res.status(403).json({

            success: false,

            message: "Access Denied"

        });

    }

    next();

};

export default admin;