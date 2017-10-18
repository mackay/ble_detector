<!doctype html>

<html lang="en">
<head>
    <meta charset="utf-8">

    <title>BLE LED Project</title>
    <meta name="description" content="BLE LED Project">
    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css" integrity="sha384-BVYiiSIFeK1dGmJRAkycuHAHRg32OmUcww7on3RYdg4Va+PmSTsz/K68vbdEjh4u" crossorigin="anonymous">
    <link rel="stylesheet" href="css/styles.css?v=1.0">


    <!-- Optional theme -->
    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap-theme.min.css" integrity="sha384-rHyoN1iRsVXV4nD0JutlnGaslCJuC7uwjduW9SVrLvRYooPp2bWYgmgJQIXwl/Sp" crossorigin="anonymous">

    <!--[if lt IE 9]>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/html5shiv/3.7.3/html5shiv.js"></script>
    <![endif]-->
</head>

<body>
    <nav class="navbar navbar-inverse navbar-fixed-top">
        <div class="container">
            <div class="navbar-header">
                <button type="button" class="navbar-toggle collapsed" data-toggle="collapse" data-target="#navbar" aria-expanded="false" aria-controls="navbar">
                    <span class="sr-only">Toggle navigation</span>
                    <span class="icon-bar"></span>
                    <span class="icon-bar"></span>
                    <span class="icon-bar"></span>
                </button>
                <a class="navbar-brand" href="#">BLE Lighting Project</a>
            </div>
            <div id="navbar" class="collapse navbar-collapse">
                <ul class="nav navbar-nav">
                    <li class="active"><a href="#">Home</a></li>
                    <li><a href="#about">About</a></li>
                    <li><a href="#contact">Contact</a></li>
                </ul>
            </div><!--/.nav-collapse -->
        </div>
    </nav>

    <div class="container">
        <div class="section">
            <h2>Mode</h2>
            <form class="form form-horizontal" accept-charset="UTF-8" role="form">
                <fieldset>
                    <div class="form-group">
                        <label for="mode" class="text-left control-label col-sm-3">Mode</label>
                        <div class="col-sm-9">
                            <select id="mode" class="form-control event-type">
                                <option value="off">Off</option>
                                <option value="run">Run</option>
                                <option value="training">Training (Beacons)</option>
                                <option value="training">Testing (Actors)</option>
                                <option value="demo">Demo</option>
                            </select>
                        </div>
                    </div>

                    <div class="form-group">
                        <label for="training-data" class="text-left control-label col-sm-3">Training / Testing Data</label>
                        <div class="col-sm-9">
                            <input id="training-data" class="form-control" placeholder="Only Used In Training or Testing Mode">
                        </div>
                    </div>
                </fieldset>
            </form>

        </div>
        <div class="section">
            <h2>Beacons</h2>
            <table class="table">
                <thead>
                    <tr>
                        <th class="col-sm-5">ID</th>
                        <th class="col-sm-3">RSSI</th>
                        <th class="col-sm-3">Last Heard</th>
                        <th class="col-sm-3">Packets</th>
                    </tr>
                </thead>

                <tbody>
                    <tr>
                        <td>90eb2126-e9ae-46ba-8d1c-8fad60a760d1</td>
                        <td>-52</td>
                        <td>2017-10-12 12:33:04</td>
                        <td>351</td>
                    </tr>
                    <tr>
                        <td>303f7849-75a8-4e1e-8f63-3eaa7fc4ca1c</td>
                        <td>-66</td>
                        <td>2017-10-12 12:32:34</td>
                        <td>12</td>
                    </tr>
                    <tr>
                        <td>b64b1bce-ebea-42f9-a1dd-3acd66877793</td>
                        <td>-23</td>
                        <td>2017-10-12 12:31:45</td>
                        <td>15235</td>
                    </tr>
                </tbody>
            </table>
        </div>
        <div class="section">
            <h2>Detectors</h2>

            <table class="table">
                <thead>
                    <tr>
                        <th class="col-sm-5">ID</th>
                        <th class="col-sm-3">Load</th>
                        <th class="col-sm-3">Last Heard</th>
                        <th class="col-sm-3">Packets</th>
                    </tr>
                </thead>

                <tbody>
                    <tr>
                        <td>Green</td>
                        <td>0.12 0.11 0.04</td>
                        <td>2017-10-12 12:33:04</td>
                        <td>3958</td>
                    </tr>
                    <tr>
                        <td>Blue</td>
                        <td>0.44 0.33 0.30</td>
                        <td>2017-10-12 12:32:34</td>
                        <td>3484</td>
                    </tr>
                    <tr>
                        <td>Black</td>
                        <td>0.10 0.10 0.10</td>
                        <td>2017-10-12 12:31:45</td>
                        <td>599</td>
                    </tr>
                </tbody>
            </table>
        </div>
        <div class="section">
            <h2>Actors</h2>

            <table class="table">
                <thead>
                    <tr>
                        <th class="col-sm-5">ID</th>
                        <th class="col-sm-3">Beacons</th>
                        <th class="col-sm-3">Last Heard</th>
                        <th class="col-sm-3">Time Active</th>
                    </tr>
                </thead>

                <tbody>
                    <tr>
                        <td>Lower Walkway</td>
                        <td><a href="#">3 Recent</a>, <a href="#">4 All Time</a></td>
                        <td>2017-10-12 12:33:04</td>
                        <td>00:23:20</td>
                    </tr>
                    <tr>
                        <td>Upper Walkway</td>
                        <td><a href="#">3 Recent</a>, <a href="#">4 All Time</a></td>
                        <td>2017-10-12 12:32:34</td>
                        <td>00:10:30</td>
                    </tr>
                </tbody>
            </table>

        </div>
    </div>
    <!-- /.container -->

    <script src="https://code.jquery.com/jquery-3.2.1.slim.min.js" integrity="sha384-KJ3o2DKtIkvYIK3UENzmM7KCkRr/rE9/Qpg6aAZGJwFDMVNA/GpGFF93hXpG5KkN" crossorigin="anonymous"></script>
    <script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/js/bootstrap.min.js" integrity="sha384-Tc5IQib027qvyjSMfHjOMaLkfuWVxZxUPnCJA7l2mCWNIpG9mGCD8wGNIcPD7Txa" crossorigin="anonymous"></script>
</body>
</html>