"""Module for retrieving and sending JSON formatted content"""
import json
"""AWS Module for interacting with AWS resources"""
import boto3
from botocore.exceptions import ClientError
import logging
import random
import math


# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize a DynamoDB session
dynamodb = boto3.resource('dynamodb')
# Create table object
table = dynamodb.Table('Metadata')
food_table = dynamodb.Table('Foods')
user_table = dynamodb.Table('Users')

def handler(event, context):
    '''
    Delegate function to handle incoming HTTP requests based on the HTTP method.
    This function supports POST, GET, PUT, and DELETE operations.
    '''
    http_method = event['httpMethod']
    logger.info(f"htttpMethod: {http_method}")

    try:
        if http_method == 'POST':
            body = json.loads(event['body'])
            logger.info(f'Event body: {body}')
            return post(body)
        elif http_method == 'GET':
            query_params = event['queryStringParameters']
            logger.info(query_params)
            return get(query_params)
        # elif http_method == 'PUT':
        #     return PUT(event.get('key'), event.get('update_expression'), \
        #             event.get('expression_attribute_values'))
        elif http_method == 'DELETE':
            body = json.loads(event['body'])
            logger.info(f'Event body: {body}')
            return delete(body)
        else:
            return format_unsuccessful_response('Unsupported HTTP method')
    except Exception as e:
        return format_unsuccessful_response(e)


def post(body: dict) -> dict:

    try: # TODO reduce size of try catch chunks

        food_id = body['id']
        # Temporary solution to add data to the tables
        if food_id == 'add_user_data':
            logger.info('Calling add_user_data()')
            add_user_data()
            return format_successful_response({'message': 'Success'})
        elif food_id == 'add_food_data':
            logger.info('Calling add_food_data()')
            add_food_data()
            return format_successful_response({'message': 'Success'})

        logger.info("User prefers %s", food_id)
        food_item_response = food_table.get_item(Key={'id': food_id})
        if 'Item' in food_item_response:
            food = food_item_response['Item']
            logger.info("Food:")
            logger.info(food.items())

        return update_user_preferences(food)
    except ClientError as e:
        return format_unsuccessful_response(e)
    except Exception as e:
        return format_unsuccessful_response(e)

def post_depricated(body: dict) -> dict:

    """
    Handles an HTTP POST request to add an item to a DynamoDB table.

    This function extracts the 'identifier' value from the provided body,
    constructs an item with attributes, and attempts to insert
    the item into the DynamoDB table.

    Parameters:
        body (dict): A dictionary containing the data sent in the POST request body.
            It must include an 'identifier' key with its associated value.

    Returns:
        dict: A dictionary with the HTTP status code and a JSON-encoded message.

    Raises:
        ClientError: If an error occurs while interacting with the DynamoDB table.
    """
    identifier_value = body['identifier']
    attribute1_value = body['attribute1']
    logger.info(f'identifier: {identifier_value}, attribute1: {attribute1_value}')

    # Temporary solution to add food data to the Foods table
    if identifier_value == 'add_food_data':
        logger.info('Calling add_food_data()')
        add_food_data()
    # Temporary solution to add user data to the User table
    if identifier_value == 'add_user_data':
        logger.info('Calling add_user_data()')
        add_user_data()

    try:
        # Add an item to the table
        dynamodb_response = table.put_item(
            Item={
                'identifier': identifier_value,
                'attribute1': attribute1_value,
            }
        )
        logger.info("DynamoDB table updated")
        return format_successful_response({'message': 'Item added to DynamoDB table successfully'})
    except ClientError as e:
        return format_unsuccessful_response(e)
    except Exception as e:
        return format_unsuccessful_response(e)

def get(query_params: dict) -> dict:

    try:
        requested_item = query_params['requested_item']
        logger.info(requested_item)

        if requested_item == 'random_food':
            return get_random_food()
        elif requested_item == 'food_suggestions':
            return get_food_suggestions()
        else:
            return format_unsuccessful_response("Invalid requested item")

    except ClientError as e:
        return format_unsuccessful_response(e)
    except Exception as e:
        return format_unsuccessful_response(e)

def get_depricated(query_params: dict) -> dict:
    """
    **Depricated**
    Retrieves an item from a DynamoDB table based on the provided identifier.

    Args:
        query_params (dict): A dictionary containing the query parameters,
            including the 'identifier' key.

    Returns:
        dict: A dictionary containing the following keys:
            - 'statusCode' (int): The HTTP status code of the response.
            - 'body' (str): The response body, which is a JSON-encoded string.

    Raises:
        ClientError: If an error occurs while interacting with the DynamoDB table.
    """
    try:
        identifier = query_params['identifier']
        logger.info(identifier)

        # Retrieve an item from the table
        dynamodb_response = table.get_item(
            Key={
                'identifier': identifier,
            }
        )
        logger.info(dynamodb_response)
        if 'Item' in dynamodb_response:
            return format_successful_response(dynamodb_response['Item'])
        else:
            return format_unsuccessful_response('Item not found in table')
    except ClientError as e:
        return format_unsuccessful_response(e)
    except Exception as e:
        return format_unsuccessful_response(e)

def delete(body: dict) -> dict:
    """
    Deletes an item from a DynamoDB table based on the provided identifier.

    Args:
        body (dict): A dictionary containing the request body, which should
            include the 'identifier' key with the value of the item to delete.

    Returns:
        dict: A dictionary containing the following keys:
            - 'statusCode' (int): The HTTP status code of the response.
            - 'body' (str): The response body, which is a JSON-encoded string.

    Raises:
        ClientError: If an error occurs while interacting with the DynamoDB table.
    """

    identifier_value = body['identifier']
    logger.info(identifier_value)
    try:
        # Add an item to the table
        response = table.delete_item(
            Key={
                'identifier': identifier_value,
            }
        )
        return format_successful_response('Item deleted successfully')
    except ClientError as e:
        return format_unsuccessful_response(e)
    except Exception as e:
        return format_unsuccessful_response(e)

# def put(key, update_expression, expression_attribute_values):
    # TODO


def add_food_data() -> None:

    # Read the contents of the file into a list
    with open('food_data.txt', 'r') as file:
        food_data = json.load(file)
        logger.info(type(food_data))
    logger.info(food_data)
    if food_data:
        logger.info('Adding food data to the Foods table')
        # Insert each food item into the 'Foods' table
        for food in food_data:
            food_table.put_item(Item=food)
            logger.info(f"Added {food['id']} to the Foods table")

def add_user_data() -> None:

    # Read the contents of the file into a list
    with open('user_data.txt', 'r') as file:
        user_data = json.load(file)
        logger.info(type(user_data))
    logger.info(user_data)
    if user_data:
        logger.info('Adding user data to the user table')
        # Insert each food item into the 'Foods' table
        for user in user_data:
            user_table.put_item(Item=user)
            logger.info(f"Added {user['id']} to the Foods table")

def format_successful_response(data: dict) -> dict:
    response = {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
        },
        'body': json.dumps(data)
    }
    return response

def format_unsuccessful_response(exception) -> dict:
    logger.exception(exception)
    response = {
        'statusCode': 500,
        'headers': {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
        },
        'body': json.dumps(f"Error: {exception}")
    }
    return response

def get_random_food() -> dict:
    """Returns a random food item from the 'Foods' table."""
    number_of_food_items_returned = 3
    try:
        # Use the scan operation to retrieve all items from the table
        response = food_table.scan()
        # Get the list of items from the response
        foods = response['Items']
        if len(foods) < number_of_food_items_returned:
            return format_unsuccessful_response("Not enough food items in the table")
        # Randomly select an item from the list
        random_items = random.sample(foods, number_of_food_items_returned)
        random_item_ids = {}
        for i, random_item in enumerate(random_items, start=1):
            logger.info(random_item['id'])
            random_item_ids[f'random_item{i}'] = random_item['id']
        return format_successful_response(random_item_ids)
    except ClientError as e:
        return format_unsuccessful_response(e)
    except Exception as e:
        return format_unsuccessful_response(e)
###############################################

def update_user_preferences(food: dict) -> dict:
    """
    Update the user's preferences in the User table based on the food item.
    """
    try:
        # Initialize parts of the update expression and expression attribute values
        update_expression = "SET "
        expression_attribute_values = {}

        for attribute, val in food.items():
            if attribute == "id" or not val:
                continue

            logger.info('%s: %s', attribute, val)
            user_attribute = map_food_to_user.get(attribute)
            if user_attribute:
                logger.info('user_attribute: %s', user_attribute)
                # Append to the update expression
                update_expression += f'preferences.{user_attribute} = preferences.{user_attribute} + :increment, '
                expression_attribute_values[':increment'] = 1

        # Append the food ID to selectedFoods
        food_id = food.get('id')
        if food_id:
            update_expression += "selectedFoods = list_append(selectedFoods, :food_id), "
            expression_attribute_values[':food_id'] = [food_id]

        # Remove the trailing comma and space from the update expression
        update_expression = update_expression.rstrip(', ')

        # Perform the update only if there are attributes to update
        if expression_attribute_values:
            user_id = 'User123'
            response = user_table.update_item(
                Key={'id': user_id},
                UpdateExpression=update_expression,
                ExpressionAttributeValues=expression_attribute_values,
                ReturnValues='UPDATED_NEW'
            )
            logger.info("Update response:")
            logger.info(response)
        else:
            logger.info("No attributes to update.")
        return format_successful_response({'message': 'Success'})
    except ClientError as e:
        return format_unsuccessful_response(e)
    except Exception as e:
        return format_unsuccessful_response(e)

def get_food_suggestions():
    try:
        number_of_suggestions = 3
        # Get the user preferences and selected foods
        user_id = 'User123'
        user_item = user_table.get_item(Key={'id': user_id}).get('Item', {})

        if not user_item:
            return format_unsuccessful_response(f"User with id {user_id} not found.")

        preferences = user_item.get('preferences', {})
        selected_foods = user_item.get('selectedFoods', [])

        # Get all food items
        food_items = food_table.scan().get('Items', [])

        if not food_items:
            return format_unsuccessful_response("No food items found.")

        suggestions = []

        for food_item in food_items:
            if food_item['id'] in selected_foods:
                continue  # Skip already selected foods

            score = 0

            for user_attr, user_weight in preferences.items():
                if user_weight == 0:
                    continue

                food_attr = get_food_from_user(user_attr)
                if food_attr and food_item.get(food_attr):
                    score += user_weight

            suggestions.append((food_item['id'], score))

        # Sort the suggestions by score in descending order
        sorted_suggestions = sorted(suggestions, key=lambda x: x[1], reverse=True)[:number_of_suggestions] # slice of top suggestions only

        # Convert sorted list into a ranked dictionary
        ranked_suggestions = {rank + 1: food for rank, (food, _) in enumerate(sorted_suggestions)}

        logger.info(ranked_suggestions)

        # Return the top three food items with the highest scores
        return format_successful_response(ranked_suggestions)
    except ClientError as e:
        return format_unsuccessful_response(e)
    except Exception as e:
        return format_unsuccessful_response(e)

def normalize_vector(vector):
    """
    Normalize a vector to have unit length.
    """
    norm = math.sqrt(sum(x ** 2 for x in vector))
    return [x / norm for x in vector] if norm > 0 else vector

def cosine_similarity(vec1, vec2):
    """
    Calculate cosine similarity between two vectors.
    """
    dot_product = sum(a * b for a, b in zip(vec1, vec2))
    norm1 = math.sqrt(sum(a ** 2 for a in vec1))
    norm2 = math.sqrt(sum(b ** 2 for b in vec2))
    return dot_product / (norm1 * norm2) if norm1 > 0 and norm2 > 0 else 0

def get_food_suggestions_test():
    try:
        number_of_suggestions = 3
        user_id = 'User123'
        user_item = user_table.get_item(Key={'id': user_id}).get('Item', {})

        if not user_item:
            return format_unsuccessful_response(f"User with id {user_id} not found.")

        preferences = user_item.get('preferences', {})
        selected_foods = set(user_item.get('selectedFoods', []))

        food_items = food_table.scan().get('Items', [])
        if not food_items:
            return format_unsuccessful_response("No food items found.")

        # Normalize user preferences
        preference_values = list(preferences.values())
        if sum(preference_values) > 0:
            normalized_preferences = normalize_vector(preference_values)
        else:
            normalized_preferences = preference_values

        suggestions = []

        for food_item in food_items:
            if food_item['id'] in selected_foods:
                continue  # Skip already selected foods

            food_vector = []
            for user_attr in preferences.keys():
                food_attr = get_food_from_user(user_attr)
                food_vector.append(food_item.get(food_attr, 0))

            # Normalize food vector
            normalized_food_vector = normalize_vector(food_vector)

            # Cosine similarity calculation
            similarity_score = cosine_similarity(normalized_preferences, normalized_food_vector)
            suggestions.append((food_item['id'], similarity_score))

        sorted_suggestions = sorted(suggestions, key=lambda x: x[1], reverse=True)[:number_of_suggestions]

        ranked_suggestions = {rank + 1: food for rank, (food, _) in enumerate(sorted_suggestions)}

        logger.info(ranked_suggestions)

        return format_successful_response(ranked_suggestions)
    except ClientError as e:
        return format_unsuccessful_response(e)
    except Exception as e:
        return format_unsuccessful_response(e)


########################################################
def get_food_from_user(target_user_attribute):
    """
    Reverse the map_food_to_user dict
    """
    for food_attribute, user_attribute in map_food_to_user.items():
        if target_user_attribute == user_attribute:
            return food_attribute

    return "key doesn't exist"

map_food_to_user = {
    "isSweet": "sweet",
    "isSalty": "salty",
    "isSour": "sour",
    "isBitter": "bitter",
    "isSpicy": "spicy",
    "isUmami": "umami",
    "isSavory": "savory",
    "isSmoky": "smoky",
    "isTangy": "tangy",
    "isRich": "rich",
    "isCrispy": "crispy",
    "isCrunchy": "crunchy",
    "isChewy": "chewy",
    "isCreamy": "creamy",
    "isTender": "tender",
    "isHighProtein": "highProtein",
    "isLowCarb": "lowCarb",
    "isGlutenFree": "glutenFree",
    "isDairyFree": "dairyFree",
    "isVegan": "vegan",
    "isGrilled": "grilled",
    "isFried": "fried",
    "isBaked": "baked",
    "isRoasted": "roasted",
    "isSteamed": "steamed",
    "isHot": "hot",
    "isCold": "cold",
    "isRoomTemperature": "roomTemperature",
    "isFrozen": "frozen",
    "isMexican": "mexican",
    "isItalian": "italian",
    "isAsian": "asian",
    "isMediterranean": "mediterranean",
    "isFusion": "fusion",
    "isComfortFood": "comfortFood",
    "isHealthy": "healthy",
    "isIndulgent": "indulgent",
    "isExotic": "exotic",
    "isOrganic": "organic"
}