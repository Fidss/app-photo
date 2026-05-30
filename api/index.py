from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
from datetime import datetime
import io
import traceback

app = Flask(__name__, template_folder="../templates")

app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024

ALLOWED_EXTENSIONS = {
    "png",
    "jpg",
    "jpeg",
    "webp"
}


def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )


def convert_to_degrees(value):
    try:
        d, m, s = value

        degrees = float(d)
        minutes = float(m)
        seconds = float(s)

        return degrees + (minutes / 60.0) + (seconds / 3600.0)

    except Exception:
        return 0


def extract_gps(gps_info):
    try:
        gps_dict = {}

        for key in gps_info:
            decoded = GPSTAGS.get(key, key)
            gps_dict[decoded] = gps_info[key]

        if (
            "GPSLatitude" in gps_dict
            and "GPSLongitude" in gps_dict
        ):
            lat = convert_to_degrees(
                gps_dict["GPSLatitude"]
            )

            lon = convert_to_degrees(
                gps_dict["GPSLongitude"]
            )

            if gps_dict.get("GPSLatitudeRef") == "S":
                lat = -lat

            if gps_dict.get("GPSLongitudeRef") == "W":
                lon = -lon

            return {
                "Latitude": lat,
                "Longitude": lon,
                "Koordinat": f"{lat:.6f}, {lon:.6f}",
                "Google Maps": f"https://maps.google.com/?q={lat},{lon}"
            }

    except Exception:
        pass

    return {}


def get_exif_data(image_bytes):
    try:
        image = Image.open(io.BytesIO(image_bytes))

        try:
            exif_data = image.getexif()
        except Exception:
            exif_data = None

        if not exif_data:
            return None

        exif_dict = {}

        for tag_id, value in exif_data.items():

            tag = TAGS.get(tag_id, tag_id)

            try:

                if tag == "DateTime":

                    dt = datetime.strptime(
                        str(value),
                        "%Y:%m:%d %H:%M:%S"
                    )

                    exif_dict["Waktu Pengambilan"] = (
                        dt.strftime("%d %B %Y, %H:%M:%S")
                    )

                    exif_dict["Tanggal Original"] = (
                        dt.strftime("%Y-%m-%d")
                    )

                    exif_dict["Waktu Original"] = (
                        dt.strftime("%H:%M:%S")
                    )

                elif tag == "DateTimeOriginal":

                    dt = datetime.strptime(
                        str(value),
                        "%Y:%m:%d %H:%M:%S"
                    )

                    exif_dict["Waktu Pengambilan"] = (
                        dt.strftime("%d %B %Y, %H:%M:%S")
                    )

                elif tag == "Model":
                    exif_dict["Perangkat"] = str(value).strip()

                elif tag == "Make":
                    exif_dict["Merek"] = str(value).strip()

                elif tag == "LensModel":
                    exif_dict["Lensa"] = str(value)

                elif tag == "ISOSpeedRatings":
                    exif_dict["ISO"] = str(value)

                elif tag == "ExposureTime":

                    try:
                        exif_dict["Kecepatan Rana"] = (
                            f"{float(value):.6f} detik"
                        )
                    except:
                        exif_dict["Kecepatan Rana"] = str(value)

                elif tag == "FNumber":

                    try:
                        exif_dict["Bukaan"] = (
                            f"f/{float(value):.1f}"
                        )
                    except:
                        exif_dict["Bukaan"] = str(value)

                elif tag == "FocalLength":

                    try:
                        exif_dict["Focal Length"] = (
                            f"{float(value):.1f} mm"
                        )
                    except:
                        exif_dict["Focal Length"] = str(value)

                elif tag == "Flash":

                    flash_dict = {
                        0: "Flash tidak menyala",
                        1: "Flash menyala"
                    }

                    exif_dict["Flash"] = (
                        flash_dict.get(
                            value,
                            str(value)
                        )
                    )

                elif tag == "WhiteBalance":

                    exif_dict["White Balance"] = (
                        "Auto"
                        if value == 0
                        else "Manual"
                    )

                elif tag == "Orientation":

                    orientation_dict = {
                        1: "Normal",
                        2: "Mirror horizontal",
                        3: "Rotate 180°",
                        4: "Mirror vertical",
                        5: "Mirror horizontal lalu rotasi 270° CW",
                        6: "Rotate 90° CW",
                        7: "Mirror horizontal lalu rotasi 90° CW",
                        8: "Rotate 270° CW"
                    }

                    exif_dict["Orientasi"] = (
                        orientation_dict.get(
                            value,
                            str(value)
                        )
                    )

                elif tag == "GPSInfo":

                    gps_data = extract_gps(value)

                    if gps_data:
                        exif_dict.update(gps_data)

                elif tag == "Software":
                    exif_dict["Software"] = str(value)

                elif tag == "Copyright":
                    exif_dict["Hak Cipta"] = str(value)

                else:

                    if (
                        tag not in exif_dict
                        and value is not None
                    ):

                        try:
                            exif_dict[str(tag)] = str(value)
                        except:
                            pass

            except Exception:
                continue

        return exif_dict

    except Exception:
        print(traceback.format_exc())
        return None


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload_file():

    if "photo" not in request.files:
        return jsonify({
            "error": "Tidak ada file yang diupload"
        }), 400

    file = request.files["photo"]

    if file.filename == "":
        return jsonify({
            "error": "File tidak dipilih"
        }), 400

    if not allowed_file(file.filename):
        return jsonify({
            "error": "Format file tidak didukung. Gunakan JPG, JPEG, PNG, WEBP"
        }), 400

    try:

        filename = secure_filename(
            file.filename
        )

        image_bytes = file.read()

        image = Image.open(
            io.BytesIO(image_bytes)
        )

        width, height = image.size

        response_data = {
            "filename": filename,
            "size": f"{len(image_bytes)/1024:.2f} KB",
            "dimensions": f"{width} x {height} px",
            "format": image.format,
            "exif": get_exif_data(image_bytes) or {}
        }

        return jsonify(response_data)

    except Exception as e:

        print(traceback.format_exc())

        return jsonify({
            "error": str(e)
        }), 500


if __name__ == "__main__":
    app.run(debug=True)
