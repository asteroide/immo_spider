SOFTWARE ARCHITECTURE

                                         -- Javascript Viewer
             [i1]           [i2]        /
    Spider ---------    ---------- APIViewer 
                    \  /                \
                RabbitMQServer           -- GTK Viewer
                 / [i3]     \ [i4]       
             DBDriver       Log
                |           |  \
                DB        File Syslog ...
            
* Spider -> DBDriver
    Data transferred to DBDriver:
    
        {
            "action": "ACTION",
            "data": {...}
        }

    `ACTION` may be:
    * `add`
        Spider send a new estate to the database
    
            {
                "action": "add",
                "data": {
                    "address": "",
                    "description": "",
                    "price": "",
                    "date": "",
                    "surface": "",
                    "groundsurface": "",
                    "url": [],
                    "photos": [],
                    "extra": {}
                }
            }

    * `delete`
        Spider asks to delete a particular estate
    
            {
                "action": "delete",
                "data": {
                    "id": ""
                }
            }

    * `get`
        Spider can retrieve a particular estate to know if it already exists
    
            {
                "action": "get",
                "data": {
                    "id": "",
                    "geoid": ""
                }
            }

* APIViewer -> DBDriver
    Data transferred to DBDriver:
    
        {
            "action": "ACTION",
            "data": {...}
        }

    `ACTION` may be:
    * `delete`
    
            {
                "action": "delete",
                "data": {
                    "id": ""
                }
            }

    * `list`
    
            {
                "action": "list"
            }

    * `get`
    
            {
                "action": "get",
                "data": {
                    "id": "",
                    "geoid": ""
                }
            }


* Spider -> Log, APIViewer -> Log, DBDriver -> Log
    Data transferred to Log:
    
        {
            "action": "ACTION",
            "data": {...}
        }

    `ACTION` may be:
    * `log`
    
            {
                "action": "log",
                "data": {
                    "source": "",
                    "datetime": "",
                    "severity": "",
                    "message": ""
                }
            }
    
        Severity can be DEBUG, INFO, WARNING, ERROR, CRITICAL

* DBDriver -> Viewer
    Data transferred to Viewer in response to an action like `add`, `delete` or `list`:
    
        {
            "action": "ACTION",
            "data": {...}
        }

    `ACTION` may be:
    * `delete`
        database deletes one estate
    
            {
                "action": "delete",
                "data": {
                    "id": "",
                    "deleted": true
                }
            }
            
        `deleted` key can be set to true or false.

    * `list`
        database sends all estates 
        
            {
                "action": "list"
                "data": [
                    {
                        "address": "",
                        "description": "",
                        "price": "",
                        "date": "",
                        "surface": "",
                        "groundsurface": "",
                        "url": [],
                        "photos": [],
                        "extra": {}
                    },
                    ...
                ]
            }

    * `get`
        database sends one or more estates 
    
            {
                "action": "get",
                "data": [
                    {
                        "address": "",
                        "description": "",
                        "price": "",
                        "date": "",
                        "surface": "",
                        "groundsurface": "",
                        "url": [],
                        "photos": [],
                        "extra": {}
                    },
                    ...
                ]
            }

