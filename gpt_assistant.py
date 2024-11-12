import os
import json
import requests
from dotenv import load_dotenv
import openai

# Tải thông tin từ .env
load_dotenv()
user_conversations = {}
class GPTAssistant:
    def __init__(self):
        # Lấy API key từ biến môi trường
        self.token = os.getenv("GITHUB_TOKEN")
        self.endpoint = "https://models.inference.ai.azure.com"
        self.model_name = "gpt-4o-mini"
        openai.api_key = self.token  # Sử dụng API key từ biến môi trường
        openai.api_base = self.endpoint  # Cấu hình endpoint
        
        # Danh sách công cụ (functions) có thể gọi
        self.tools = [
            {
                "name": "get_rooms",  
                "description": "Get list of available rooms",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "searchByLocation",
                "description": "Search for rooms by location",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "The location to search for rooms example: Việt nam, Hà Nội, ..." 
                        }
                    },
                    "required": ["location"]
                }
                },
            {
                "name": "informationOfroom",
                "description": "Get information of a room",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "room_name": {
                            "type": "string",
                            "description": "The name of the room to get information"
                        }
                    },
                    "required": ["room_name"]
                }
                },
            {
                "name": "get_users",  
                "description": "Get list of users",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "currency_conversion",
                "description": "Convert an amount of money from one currency to another",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "amount": {
                            "type": "number",
                            "description": "The amount of money to convert"
                        },
                        "from_currency": {
                            "type": "string",
                            "description": "The currency to convert from such as: USD, VND, EURO, ..."
                        },
                        "to_currency": {
                            "type": "string",
                            "description": "The currency to convert to such as: USD, VND, EURO, ..."
                        }
                    },
                    "required": ["amount", "from_currency", "to_currency"]
                    
            }}
        ]
        
        # Danh sách hàm tương ứng với công cụ
        self.function_map = {
            "get_rooms": self.get_rooms,
            "get_users": self.get_users,
            "currency_conversion": self.currency_conversion,
            "searchByLocation": self.searchByLocation,
            "informationOfroom": self.informationOfroom
            # Bạn có thể thêm hàm mới vào đây tương ứng với công cụ
        }
        
    def informationOfroom(self, room_name: str) -> str:
        """Lấy thông tin chi tiết của phòng từ API"""
        try:
            response = requests.get(f"http://localhost:5000/api/v1/ai/search/{room_name}")
            data = response.json()
            print("Dữ liệu phòng:", data)
            
            # Kiểm tra xem phòng có tồn tại trong API hay không
            if isinstance(data, dict) and data.get("message") == "Room not found":
                return f"Không tìm thấy phòng {room_name}. Bạn có thể thử tìm kiếm phòng khác."
            
            # Kiểm tra và lấy thông tin phòng
            if isinstance(data, dict) and "name" in data:
                room_name = data.get("name", "Không có tên phòng")
                room_price = data.get("price", "Không có giá")
                room_location = data.get("location", "Không có vị trí")
                room_description = data.get("description", "Không có mô tả")
                room_services = data.get("services", {})
                room_facilities = room_services.get("facilities", [])
                room_service = room_services.get("service", [])
                room_bathroom = room_services.get("bathroom", [])
                
                # Chuẩn bị thông tin phòng trả về
                room_info = f"Thông tin phòng: {room_name}\n"
                room_info += f"Mô tả: {room_description}\n"
                room_info += f"Giá: {room_price} VND\n"
                room_info += f"Vị trí: {room_location}\n"
                room_info += f"Dịch vụ:\n"
                room_info += f"  - Tiện nghi: {', '.join(room_facilities) if room_facilities else 'Không có tiện nghi'}\n"
                room_info += f"  - Dịch vụ phòng: {', '.join(room_service) if room_service else 'Không có dịch vụ phòng'}\n"
                room_info += f"  - Phòng tắm: {', '.join(room_bathroom) if room_bathroom else 'Không có thông tin phòng tắm'}\n"
                
                return room_info
            
            return f"Không có dữ liệu hợp lệ từ API."
        
        except requests.RequestException as e:
            return f"Không thể lấy thông tin phòng: {str(e)}"
        
            
    def searchByLocation(self, location: str) -> str:
        """Tìm kiếm phòng theo vị trí"""
        try:
            # Truyền location vào API
            response = requests.get(f"http://localhost:5000/api/v1/ai/search/location?location={location}")
            data = response.json()
            
            print("Dữ liệu phòng:", data)
            
            # Kiểm tra nếu dữ liệu trả về là một dict và chứa thông báo lỗi
            if isinstance(data, dict) and data.get("message") == "Không tìm thấy phòng theo vị trí này":
                return f"Không tìm thấy phòng nào ở {location}. Bạn có thể thử tìm kiếm phòng ở khu vực khác như Hà Nội hoặc Thành phố Hồ Chí Minh."
            
            # Kiểm tra nếu dữ liệu trả về là một list và có phòng
            if isinstance(data, list) and data:
                room_names = [room["name"] for room in data if isinstance(room, dict) and "name" in room]
                return ",".join(room_names) if room_names else f"Không có phòng nào ở {location}."
            
            # Nếu dữ liệu không phải là list hoặc không có phòng
            return f"Không có dữ liệu hợp lệ từ API."

        except requests.RequestException as e:
            return f"Không thể tìm kiếm phòng: {str(e)}"

        
    def gpt_response(self):
        """Gửi yêu cầu đến OpenAI API để nhận phản hồi từ mô hình GPT-4o-mini"""
        try:
            response = openai.ChatCompletion.create(
                model=self.model_name,
                messages=[{
                    "role": "system", 
                    "content": "Bạn là trợ lý giúp người dùng lấy thông tin về các phòng, người dùng, và các phản hồi từ GPT."
                }]
            )
            return response["choices"][0]["message"].get("content", "Không có nội dung trong phản hồi.")
        except Exception as e:
            return f"Đã xảy ra lỗi: {str(e)}"
    
    def get_rooms(self):
        """Lấy danh sách các phòng và chỉ trả về tên phòng"""
        try:
            response = requests.get("http://localhost:5000/api/v1/rooms")
            data = response.json()
            
            
            # Trả về danh sách tên phòng
            room_names = [room["name"] for room in data]
            return room_names
        except requests.RequestException as e:
            return f"Không thể lấy danh sách phòng: {str(e)}"
        
    def get_users(self):
        """Lấy danh sách người dùng từ dữ liệu mặc định"""
        # Dữ liệu giả lập người dùng
        mock_users = [
            {"name": "Nguyễn Văn A", "email": "a@example.com"},
            {"name": "Trần Thị B", "email": "b@example.com"},
            {"name": "Lê Văn C", "email": "c@example.com"},
            {"name": "Phạm Thị D", "email": "d@example.com"}
        ]
        
        # Trả về danh sách tên người dùng
        user_names = [user["name"] for user in mock_users]
        return user_names
    def currency_conversion(self, amount: float, from_currency: str, to_currency: str) -> str:
            """Convert an amount of money from one currency to another.
            amount: float - the amount of money to convert
            from_currency: str - the currency to convert from such as: USD, VND, EURO, ...
            to_currency: str - the currency to convert to such as: USD, VND, EURO, ...
            """
            data = requests.get(f"https://v6.exchangerate-api.com/v6/fca802c1f0bc455e994dfa0b/latest/{from_currency}")
            exchange_rate = data.json()["conversion_rates"].get(to_currency)
            if exchange_rate:
                converted_amount = amount * exchange_rate
                return f"{amount} {from_currency} is equal to {converted_amount} {to_currency}"
            else:
                return f"Không thể chuyển đổi từ {from_currency} sang {to_currency}"
        
    def process_message(self, user_message: str, user_id: str):
        """Xử lý tin nhắn người dùng và trả lời từ GPT hoặc gọi công cụ"""

        # Khởi tạo hội thoại cho người dùng nếu chưa có trong lịch sử
        if user_id not in user_conversations:
            user_conversations[user_id] = []

        # Lấy lịch sử hội thoại của người dùng
        conversation_history = user_conversations[user_id]

        # Thêm tin nhắn của người dùng vào lịch sử
        conversation_history.append({"role": "user", "content": user_message})
        print("Lịch sử hội thoại hiện tại:", conversation_history)

        try:
            # Tạo yêu cầu cho OpenAI API với tham số 'functions' nếu cần gọi công cụ
            response = openai.ChatCompletion.create(
                model=self.model_name,
                messages=conversation_history,
                functions=self.tools
            )

            # Kiểm tra nếu phản hồi có chứa gọi công cụ
            if "choices" in response and len(response["choices"]) > 0:
                choice = response["choices"][0]
                if "message" in choice and "function_call" in choice["message"]:
                    function_call = choice["message"]["function_call"]

                    # Lấy tên và tham số công cụ từ function_call
                    function_name = function_call["name"]
                    function_args = function_call.get("arguments", {})
                    print("function_args:", function_args)
                    print("function_name:", function_name)
                    if isinstance(function_args, str):
                        try:
                            function_args = json.loads(function_args)  # Chuyển đổi chuỗi thành từ điển
                        except json.JSONDecodeError:
                            return "Lỗi: Dữ liệu không hợp lệ cho function_args."

                    if "location" in function_args:
                        location = function_args["location"]
                        return self.searchByLocation(location)
                    if "room_name" in function_args:
                        room_name = function_args["room_name"]
                        return self.informationOfroom(room_name)

                    # Gọi công cụ cụ thể dựa trên tên công cụ
                    if function_name == "currency_conversion":
                        amount = function_args.get("amount")
                        from_currency = function_args.get("from_currency")
                        to_currency = function_args.get("to_currency")

                        # Kiểm tra các tham số
                        if amount is None or from_currency is None or to_currency is None:
                            return "Vui lòng cung cấp đầy đủ thông tin cho currency_conversion."

                        # Thực hiện chức năng chuyển đổi tiền tệ
                        result = self.currency_conversion(amount, from_currency, to_currency)

                    elif function_name in self.function_map:
                        result = self.function_map[function_name]()  # Gọi hàm tương ứng

                    # Chuyển đổi kết quả thành chuỗi nếu là danh sách
                    result_text = result if isinstance(result, str) else ",".join(result)

                    # Thêm kết quả công cụ vào lịch sử hội thoại
                    conversation_history.append(
                        {
                            "role": "assistant",
                            "content": result_text
                        }
                    )
                    print("Lịch sử hội thoại sau khi gọi công cụ:", conversation_history)

                    # Gửi lại yêu cầu với lịch sử đã cập nhật
                    response = openai.ChatCompletion.create(
                        model=self.model_name,
                        messages=conversation_history
                    )

                    print("Phản hồi sau khi gọi công cụ:", response)
                    # Trả về nội dung từ phản hồi cuối
                    return response["choices"][0]["message"].get("content", "Không có nội dung trong phản hồi.")
            
            # Nếu không có công cụ nào phù hợp, trả về phản hồi từ GPT trực tiếp
            assistant_message = response["choices"][0]["message"]["content"]
            
            # Thêm phản hồi của assistant vào lịch sử hội thoại
            conversation_history.append(
                {
                    "role": "assistant",
                    "content": assistant_message
                }
            )
            print("Lịch sử hội thoại sau khi GPT trả lời:", conversation_history)

            return assistant_message

        except Exception as e:
            return f"Đã xảy ra lỗi: {str(e)}"


