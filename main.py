from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv
import os
# আমরা সরাসরি মোটরের অ্যাসিনক্রোনাস ক্লায়েন্ট ব্যবহার করছি
from motor.motor_asyncio import AsyncIOMotorClient

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
client = AsyncIOMotorClient(MONGO_URI)
db = client["students"]
stu_collection = db["students_coll"]

app = FastAPI()

class Student(BaseModel):
    id: int
    name: str
    phone: str  # আমি এটিকে str করে দিয়েছি যেন ০ দিয়ে শুরু হওয়া ফোন নম্বর এরর না দেয়
    city: str
    course: str

# ১. এখানে 'async def' ব্যবহার করতে হবে
@app.post("/add_student")
async def stu_collection_insert_helper(student: Student):
    # ২. Pydantic অবজেক্টকে ডিকশনারিতে রূপান্তর করতে হবে
    student_dict = student.model_dump() 
    
    # ৩. মোটরের জন্য অবশ্যই 'await' ব্যবহার করতে হবে
    result = await stu_collection.insert_one(student_dict)
    
    return str(result.inserted_id)


@app.get("/get_students")
async def get_student_helper():
    students = await stu_collection.find({}).to_list(length=None)  # আমরা সব ডকুমেন্ট পেতে চাই, তাই length=None ব্যবহার করেছি
    for student in students:
        student["_id"] = str(student["_id"])  # MongoDB এর ObjectId কে স্ট্রিং এ রূপান্তর করা হচ্ছে
    return students
