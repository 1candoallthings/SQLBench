import os

SECRETKEYS = {
    'llama2': [
        "10.119.25.63", 
        "10.119.22.197",
        "10.119.27.222"
    ],
    'codellama': [
        "10.119.17.70", 
        "10.119.17.234",
        "10.119.18.29",
        "10.119.18.75"
    ]
    
}
root_path = os.path.dirname(os.path.abspath(__file__))
DATABASE_PATH=os.path.join(root_path, 'utils/database-spider/database-dev')
