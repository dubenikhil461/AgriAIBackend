import express from 'express'
const app = express.Router()

import cropRoute from './routes/cropsPredict.js' 
app.use('/f',cropRoute)

export default app