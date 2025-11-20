<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Картинка</title>
    <style>
        .image-card {
            border: 1px solid #ccc;
            padding: 10px;
            margin: 10px;
            display: inline-block;
        }
        .image-card img {
            width: 200px;
            height: 150px;
        }
    </style>
</head>
<body>
    <form method="POST">
        <button name="show_images" type="submit">Картинка</button>
        <input type="hidden" name="show_images" value="<?php echo isset($_POST['show_images']) && $_POST['show_images'] == '1' ? '0' : '1'; ?>">
    </form>

    <?php
    // подклбючение к бд
   if( isset($_POST['show_images']) && $_POST['show_images'] == '1' ){
        $host = 'localhost';       
        $dbname = 'postgres';         
        $username = 'postgres';   
        $password = '123456';
        
        try {
            $pdo = new PDO("pgsql:host=$host;dbname=$dbname", $username, $password);
            
            // выводим картинку
            $result = $pdo->query("SELECT * FROM images");
            
            while($row = $result->fetch()) {
    echo '<div class="image-card">';
    echo '<img src="'.$row['image_url'].'" alt="Картинка">';
    echo '<div>Картинка</div>';
    echo '</div>';
}
            
        } catch(Exception $e) {
            echo "Ошибка: " . $e->getMessage();
        }
    }
    ?>
</body>
</html>
