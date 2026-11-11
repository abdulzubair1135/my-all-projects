// ==========================================================
//
// FILE : password.helper.js
//
// PURPOSE
// --------
// Password Hash aur Verify
//
// ==========================================================

import bcrypt from "bcrypt";

// ================================================
// HASH PASSWORD
// ================================================

export const hashPassword = async (password) => {

    return await bcrypt.hash(

        password,

        10

    );

};

// ================================================
// VERIFY PASSWORD
// ================================================

export const comparePassword = async (

    password,

    hash

) => {

    return await bcrypt.compare(

        password,

        hash

    );

};