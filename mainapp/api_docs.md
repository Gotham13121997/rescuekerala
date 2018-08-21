## Available Endpoints

### GET /data

Returns paginated requests from the mainapp_requests table.

Response format:

```
{
  "data": [
    {
      "id": 1,
      "district": "idk",
      "location": "asd",
      "requestee": "ads",
      "requestee_phone": "04772239305",
      "latlng": "37.3880437,-121.996404",
      "latlng_accuracy": "23 Meters",
      "is_request_for_others": false,
      "needwater": false,
      "needfood": false,
      "needcloth": false,
      "needmed": false,
      "needtoilet": false,
      "needkit_util": true,
      "needrescue": false,
      "detailwater": "",
      "detailfood": "",
      "detailcloth": "",
      "detailmed": "",
      "detailtoilet": "",
      "detailkit_util": "",
      "detailrescue": "",
      "needothers": "",
      "status": "new",
      "supply_details": "",
      "dateadded": "2018-08-20T07:24:29.857Z"
    }
  ],
  "meta": {
    "offset": 0,
    "limit": 300,
    "description": "select * from mainapp_requests where id > offset order by id limit 300",
    "last_record_id": 1
  }
}
```

### POST /request_data/

Example Request:

```
Content-Type:application/json

POST http://localhost:8000/request_update/

{
  "status": 'pro',
  "updater_name": "cbin" ,
  "updater_phone": "+919647477846",
  "notes": "some random test string",
  "request": "6777"
}

```

Available statuses:

* `hig`: 'High priority'
* `med`: 'Medium priority'
* `low`: 'Low priority'
* `cls`: 'Can be closed'
* `otr`: 'Other'

Expecting 3rd parties to use one of the priorities or `cls` to feed back status after resolution/filtering, and otr in case there's an update that doesn't fit one of these statuses.
