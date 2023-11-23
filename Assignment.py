import random
import json 
import boto3
import configparser

config = configparser.ConfigParser()
config.read('.config')

aws_access_key_id = config.get('aws_credentials', 'aws_access_key_id')
aws_secret_access_key = config.get('aws_credentials', 'aws_secret_access_key')


# parking lot class that takes in a square footage size as input
class ParkingLot:
    def __init__(self, square_footage, spot_size=(8, 12)):
        self.square_footage = square_footage
        self.spot_size = spot_size
        self.max_cars = self.maximum_cars_calculation()

        # Initialize parking lot array with empty spots
        self.parking_lot = [None] * self.max_cars
        #Initialize vehicle mapping with empty dictionary
        self.vehicle_mapping = {}

    def maximum_cars_calculation(self):
        spot_area = self.spot_size[0] * self.spot_size[1]
        print("Total number of cars will be spot to park",self.square_footage // spot_area)
        return self.square_footage // spot_area
    
    def map_vehicles_to_spots(self):
        for spot, vehicle in enumerate(self.parking_lot):
            if vehicle:
                self.vehicle_mapping[vehicle.license_plate] = spot

    def save_mapping_to_json(self, file_path):
        with open(file_path, 'w') as file:
            json.dump(self.vehicle_mapping, file)
#Function for upload json data in S3 Bucket
def upload_to_s3(file_path, bucket_name, object_key):
    s3 = boto3.client('s3', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)
    s3.upload_file(file_path, bucket_name, object_key)

#car class that takes in a 7 digit license plate and sets it as a property
class Car:
    def __init__(self, license_plate):
        self.license_plate = license_plate

    def __str__(self):
        return f"Car with license plate {self.license_plate}"

    def park(self, parking_lot, spot):
        if parking_lot.parking_lot[spot] is None:
            parking_lot.parking_lot[spot] = self
            return f"{self} parked successfully in spot {spot}"
        else:
            return f"Failed to park {self} in spot {spot}. Spot is already occupied."

def main():
    input_square_footage=int(input("Enter Square Footage: "))
    parking_lot = ParkingLot(square_footage=input_square_footage)

    # Create an array of cars with random license plates
    cars = [Car(f"{random.randint(1000000, 9999999)}") for _ in range(parking_lot.max_cars)]

    # Park cars in the parking lot until it's full or no more cars
    for spot in range(parking_lot.max_cars):
        if not cars:
            print("No more cars to park. Exiting.")
            break

        car = random.choice(cars)
        status = car.park(parking_lot, spot)
        print(status)

        # Remove the parked car from the list when car is slotted for parking
        cars.remove(car)

    # Map vehicles to spots and save to JSON file
    parking_lot.map_vehicles_to_spots()
    parking_lot.save_mapping_to_json('vehicle_mapping.json')

    # Upload the JSON file to S3
   # upload_to_s3('vehicle_mapping.json', 'bucket2', 'vehicle_mapping.json') # Here change the bucket name 

if __name__ == "__main__":
    main()
