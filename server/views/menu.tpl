<!doctype html>

<html lang="en">
<head>
    <meta charset="utf-8">

    <title>BLE LED Project</title>
    <meta name="description" content="BLE LED Project">
    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css" integrity="sha384-BVYiiSIFeK1dGmJRAkycuHAHRg32OmUcww7on3RYdg4Va+PmSTsz/K68vbdEjh4u" crossorigin="anonymous">
    <link rel="stylesheet" href="css/toastr.css?v=1.0">
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
            <h2>Operation</h2>
            <form class="form form-horizontal" accept-charset="UTF-8" role="form">
                <fieldset>
                    <div class="form-group">
                        <label for="mode" class="text-left control-label col-sm-3">Mode</label>
                        <div class="col-sm-9">
                            <select id="mode" class="form-control event-type">
                                <option value="off">Off</option>
                                <option value="run">Run</option>
                                <option value="training">Training (Beacons)</option>
                                <option value="testing">Testing (Actors)</option>
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

                    <div class="form-group">
                        <label for="filter-data" class="text-left control-label col-sm-3">Beacon Filter</label>
                        <div class="col-sm-9">
                            <input id="filter-data" class="form-control" placeholder="Only Allow UUIDs With This String">
                        </div>
                    </div>
                    <div class="form-group">
                        <div class="col-sm-offset-3 col-sm-9">
                            <div class="checkbox">
                                <label>
                                    <input id="refresh" type="checkbox" checked> Automatic Refresh (5 seconds)
                                </label>
                            </div>
                        </div>
                    </div>
                </fieldset>
            </form>
        </div>
        <div class="section beacon">
            <h2>Beacons</h2>
            <table class="table">
                <thead>
                    <tr>
                        <th class="col-sm-8">ID</th>
                        <th class="col-sm-3">Last Heard</th>
                        <th class="col-sm-3">Packets</th>
                    </tr>
                </thead>

                <tbody></tbody>
            </table>
        </div>
        <div class="section detector">
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

                <tbody></tbody>
            </table>
        </div>
        <div class="section agent">
            <h2>Agents</h2>

            <table class="table">
                <thead>
                    <tr>
                        <th class="col-sm-6">ID</th>
                        <th class="col-sm-4">Last Heard</th>
                        <th class="col-sm-4">Time Active (hrs)</th>
                    </tr>
                </thead>

                <tbody>
                </tbody>
            </table>
        </div>

        <div class="section reset">
            <h2>Reset</h2>
            <div class="btn btn-danger" resource="training">Delete Training Data</div>
            <div class="btn btn-danger" resource="signal">Delete Signal Data</div>
            <div class="btn btn-danger" resource="beacon">Delete Beacon Data</div>
            <div class="btn btn-danger" resource="detector">Delete Detector Data</div>
            <div class="btn btn-danger" resource="agent">Delete Agent Data</div>
    </div>
    <!-- /.container -->

    <script src="https://code.jquery.com/jquery-3.2.1.min.js" crossorigin="anonymous"></script>
    <script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/js/bootstrap.min.js" crossorigin="anonymous"></script>

    <script src="./js/underscore-min.js"></script>
    <script src="./js/extend.js"></script>
    <script src="./js/toastr.min.js"></script>
    <script src="./js/my.class.min.js"></script>
    <script src="./js/pinocchio.js"></script>
    <script src="./js/moment.min.js"></script>
    <script src="./js/scripts.js"></script>
</body>
</html>