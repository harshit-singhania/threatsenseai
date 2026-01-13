import { asyncHandler } from "../utils/asyncHandler.js";
import {ApiError} from "../utils/ApiError.js"
import { ApiResponse } from "../utils/ApiResponse.js";
import { pool } from "../db/index.js";
import crypto from "crypto";

const registerUser = asyncHandler( async (req, res) => {
    const {name, email, message} = req.body

    if ([name, email].some((field) => field?.trim() === "")) {
        throw new ApiError(400, "Name and Email are required")
    }

    // Check if user exists
    const userCheck = await pool.query('SELECT * FROM users WHERE email = $1', [email]);
    
    if (userCheck.rows.length > 0) {
        return res.status(200).json(
            new ApiResponse(200, { user_id: userCheck.rows[0].id }, "User already exists")
        )
    }

    // Generate UUID like Python's uuid.uuid4()
    const id = crypto.randomUUID();

    // Insert new user
    // Note: Assuming 'users' table exists as created by Flask-Migrate
    const query = 'INSERT INTO users (id, name, email, created_at) VALUES ($1, $2, $3, NOW()) RETURNING *';
    const values = [id, name, email];

    const result = await pool.query(query, values);
    const user = result.rows[0];

    return res.status(201).json(
        new ApiResponse(200, { user_id: user.id, ...user }, "User registered Successfully")
    )

})

export {registerUser}