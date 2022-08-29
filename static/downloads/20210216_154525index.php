<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta charset="utf-8" />
        <meta http-equiv="X-UA-Compatible" content="IE=edge" />
        <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no" />
        <meta name="description" content="" />
        <meta name="author" content="" />
        <title>Dealer Login</title>
        <link href="css/styles.css" rel="stylesheet" />
        <script src="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.1/js/all.min.js" crossorigin="anonymous"></script>
<style>
body {
  font-family: Arial;
  color: white;
}

.split {
  height: 100%;
  width: 50%;
  position: fixed;
  z-index: 1;
  top: 0;
  overflow-x: hidden;
  padding-top: 20px;
}

.left {
  left: 0;
  background-color:;
}

.right {
  right: 0;
  background-color:#99cccc ;
}
.center {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 30px;
  
  
}
#login{
  
}
.centered {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  text-align: center;
}

.centered img {
  width: 500px;
  border-radius: ;
}
</style>
</head>
<body>

<div class="split left">
  <div class="centered">
    <img src="logo-new.png"  width="300px">
    
  </div>
</div>

<div class="split right">

<div align="left">
<div class="col-md-12">
<div class="form-group">
                                        
                                        </div>
                                        
                                        <form method="POST" action="loginAction.php">
                                        <div class="card-body">
                                        <div id="login">
                                       
                                        <div class="card-header">
                                     <div class="form-group">
                                        <img src="kni_logo.png" width="350px" class="img-circle" class="img-responsive">
                                        </div>

                                        <div class="col-md-12">
                                        
                                            <div class="form-group">
                                                <label class="small mb-1" for="inputEmailAddress">Username</label>
                                                <input class="form-control py-4" id="inputEmailAddress" type="text" placeholder="Enter email address" name="user"/>
                                            </div>
                                            <div class="form-group">
                                                <label class="small mb-1" for="inputPassword">Password</label>
                                                <input class="form-control py-4" id="inputPassword" type="password" placeholder="Enter password" name="pass" />
                                            </div>
                                            <div class="form-group">
                                                <div class="custom-control custom-checkbox">
                                                    <input class="custom-control-input" id="rememberPasswordCheck" type="checkbox" />
                                                    <label class="custom-control-label" for="rememberPasswordCheck">Remember password</label>
                                                </div>
                                            </div>
                                            <div class="form-group d-flex align-items-center justify-content-between mt-4 mb-0">
                                                
                                                <input type="submit" value="Login">
                                            </div>
                                            </div>
                                           </div>
                                           </div>
                                        </form>
                                        </div>
                                    </div>
                                    </div>
<script src="https://code.jquery.com/jquery-3.5.1.slim.min.js" crossorigin="anonymous"></script>
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@4.5.3/dist/js/bootstrap.bundle.min.js" crossorigin="anonymous"></script>
        <script src="js/scripts.js"></script>

</body>
</html> 
