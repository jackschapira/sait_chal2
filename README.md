# Instructions for participants of kit tracker challenge

There are 27 pieces of (simulated) optech kit deployed in various locations around the world.

## kit_info.csv

-   kit_info.csv is provided alongside the README in this repo, it contains information about all deployed optech kit. Only constant/ unchanging information, recorded when devices were intially deployed has been registered. Current status information can only be recieved from the devices themselves.

    -   This is the only data source you will need to read if you only wish to complete the MUST requirements of this challenge.

## Device broadcast

-   They have been configured on deployment to broadcast status and any captured information (if applicable) approximately every minute. This information will change over time with each broadcast eg. battery will decrease over time. Every ~30 minutes device information will be reset back to default values.

    -   Let us know if you intend to complete this challenge. We will need your devices IP to enable the deployed kit to broadcast to you.

    -   They will broadcast POST requests to your devices port 8000, on endpoint /device_rx.

    -   You will recieve requests in the following schema:

    ```js
       Device = {
            serial: str
            type: str
            model: str
            op: str
            deployed: str
            description: str
            location: str
            mgrs: str
            mobile: bool
            online: bool
            tampered: bool
            battery: int
            // If type is camera, payload will be a .jpg image
            // encoded as a byte string, else None
            payload: Optional[str]
       }
    ```

## Device recieve

-   Each device also forwards the latest copy of it's broadcasted data to an API on the LAN. You could demonstrate your solutions ability to communicate with deployed devices by querying this API.

    -   You will be provided the API IP upon request

    -   To query, you will need to submit a GET request to port 8000 on the API IP, using endpoint /device_tx/{serial} where {serial} is the serial number of the device you wish to query

    -   If an incorrect serial is provided, or the device is offline, a 404 will be returned

    -   Otherwise, a 200 will be returned with device information in the same schema as above
