import sys
import math
import signal
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtGui import QPainter, QColor
from PyQt5.QtCore import Qt, QTimer

class InertialModel2D:
	"""
	A 2D inertial model representing an object with speed, angle, position, and the ability to apply force.

	Attributes:
		x (float): x-coordinate of the object's position.
		y (float): y-coordinate of the object's position.
		speed (float): Current speed of the object.
		angle (float): Current angle of the object (in radians, 0 = right, pi/2 = up, etc.).
		mass (float): Mass of the object (affects inertia).
		friction (float): Friction coefficient (reduces speed over time).
		vx (float): Velocity in the x-direction.
		vy (float): Velocity in the y-direction.
	"""

	def __init__(self, x=0.0, y=0.0, speed=0.0, angle=0.0, mass=1.0, friction=0.05):
		"""
		Initializes the InertialModel2D.

		Args:
			x (float): Initial x-coordinate.
			y (float): Initial y-coordinate.
			speed (float): Initial speed.
			angle (float): Initial angle (in radians).
			mass (float): Mass of the object.
			friction (float): Friction coefficient (0.0 - 1.0, where 0.0 is no friction and 1.0 is high friction).
		"""
		self.x = x
		self.y = y
		self.speed = speed
		self.angle = angle
		self.mass = mass
		self.friction = friction
		self.vx = speed * math.cos(angle)
		self.vy = speed * math.sin(angle)

	def applyForce(self, force, force_angle):
		"""
		Applies a force to the object, affecting its speed and direction.

		Args:
			force (float): Magnitude of the force.
			force_angle (float): Angle of the force (in radians).
		"""
		# Resolve force into x and y components
		fx = force * math.cos(force_angle)
		fy = force * math.sin(force_angle)

		# Calculate acceleration
		ax = fx / self.mass
		ay = fy / self.mass

		# Update velocity
		self.vx += ax
		self.vy += ay

		# Update speed and angle based on new velocity
		self.speed = math.sqrt(self.vx**2 + self.vy**2)
		self.angle = math.atan2(self.vy, self.vx)

	def update(self, dt=0.1):
		"""
		Updates the object's position and speed based on its current state and applied forces.
		Includes friction to slow down the object over time.

		Args:
			dt (float): Time step (in seconds).
		"""
		# Apply friction
		self.vx *= (1 - self.friction * dt)
		self.vy *= (1 - self.friction * dt)

		# Update speed and angle based on new velocity after friction
		self.speed = math.sqrt(self.vx**2 + self.vy**2)

		# Handle very low speed to prevent jittering
		if self.speed < 0.001:
			self.speed = 0
			self.vx = 0
			self.vy = 0

		if self.speed != 0: #avoid errors when speed is exactly 0
			self.angle = math.atan2(self.vy, self.vx)


		# Update position
		self.x += self.vx * dt
		self.y += self.vy * dt

	def __str__(self):
		return f"Position: ({self.x:.2f}, {self.y:.2f}), Speed: {self.speed:.2f}, Angle: {math.degrees(self.angle):.2f}°"

class Truck:
	def __init__(self, initial_pos, truck_dimensions, color=QColor(255,0,0),
				 axles=None):
		self.x = float(initial_pos[0]);
		self.y = float(initial_pos[1]);

		self.inModel = InertialModel2D(x=self.x, y=self.y, speed=0, angle=0, mass=1.0, friction=20)

		self.width = float(truck_dimensions[1]);
		self.length = float(truck_dimensions[0]);

		self.angle = 0;

		self.linearSpeed = 1.0;
		# Degrees per second
		self.angularSpeed = 90.0;

		self.throttle = 0;

		self.color = color;
		self.speed = 0;

		self.maxSteeringAngle = 40.0;
		self.steeringAngle = 40.0;
		self.wheelDiameter = 20.0;

		self.axleWidth = 5.0 # For drawing purposes only
		if axles:
			self.wheelBase = axles[0]
			self.wheelThread = axles[1]
			self.wheelBaseOffset = axles[2]
		else:
			self.wheelBase = self.length * 0.7
			self.wheelTread = self.width
			self.wheelBaseOffset = 0.0 #Shifts the wheels forward

	def setSteering(self, steering):
		self.steeringAngle = self.maxSteeringAngle * steering

	def getSteering(self):
		return self.steeringAngle / self.maxSteeringAngle

	def drawTruck(self, painter):
		# Set the color and draw the rectangle
		painter.save()

		painter.setPen(Qt.black)
		painter.setBrush(self.color)

		painter.translate(int(self.x), int(self.y))
		painter.rotate(self.angle)
		# Draw rectangle centered at origin
		painter.drawRect(int(-self.length/2),
						 int(-self.width/2),
						 int(self.length),
						 int(self.width))

		painter.restore()

	def drawAxles(self, painter, color=Qt.black):
		painter.save()

		painter.setPen(Qt.black)
		painter.setBrush(color)

		painter.translate(int(self.x), int(self.y))
		painter.rotate(self.angle)

		painter.drawRect(int(self.wheelBaseOffset-(self.wheelBase/2)),
						 int(-self.axleWidth/2),
						 int(self.wheelBase),
						 int(self.axleWidth))

		painter.translate(int(self.wheelBaseOffset+(self.wheelBase/2)),0)
		painter.drawRect(int(-self.axleWidth/2),
						 int(-self.wheelTread/2),
						 int(self.axleWidth),
						 int(self.wheelTread))
		self.drawFrontWheels(painter)
		painter.translate(-self.wheelBase,0)

		#Draw rear axle components
		painter.drawRect(int(-self.axleWidth/2),
						 int(-self.wheelTread/2),
						 int(self.axleWidth),
						 int(self.wheelTread))
		self.drawRearWheels(painter)

		painter.restore()

	def drawFrontWheels(self, painter):
		'''
			Draws the front wheels. Must be called from the rear axle
			transformation to work correctly.
		'''
		painter.save()
		painter.translate(0, -self.wheelTread/2+self.axleWidth/2)
		painter.rotate(self.steeringAngle)

		painter.drawRect(int(-self.wheelDiameter/2),
						 int(-self.axleWidth/2),
						 int(self.wheelDiameter),
						 int(self.axleWidth))
		painter.restore()

		painter.save()
		painter.translate(0, self.wheelTread/2-self.axleWidth/2)
		painter.rotate(self.steeringAngle)

		painter.drawRect(int(-self.wheelDiameter/2),
						 int(-self.axleWidth/2),
						 int(self.wheelDiameter),
						 int(self.axleWidth))
		painter.restore()

	def drawRearWheels(self, painter):
		'''
			Draws the rears wheels. Must be called from the rear axle
			transformation to work correctly.
		'''

		painter.drawRect(int(-self.wheelDiameter/2),
						 int(-self.wheelTread/2),
						 int(self.wheelDiameter),
						 int(self.axleWidth))

		painter.drawRect(int(-self.wheelDiameter/2),
						 int(self.wheelTread/2-self.axleWidth),
						 int(self.wheelDiameter),
						 int(self.axleWidth))

		#painter.restore()

	def tick(self, dt):

		#self.angular_speed * dt

		self.inModel.applyForce(self.linearSpeed * self.throttle * dt *10000,
								math.radians(self.angle))

		self.inModel.update(dt)

		self.x = self.inModel.x
		self.y = self.inModel.y
		print(self.inModel)

		#distance = self.linearSpeed * self.throttle * dt
		#rad = math.radians(self.angle)
		#delta_x = distance * math.cos(rad)
		#delta_y = distance * math.sin(rad)
		#self.x += delta_x
		#self.y += delta_y

	def getSpeed(self):
		return self.linearSpeed * self.throttle

	def setThrottle(self, throttle):
		self.throttle = throttle

	def setAngle(self, angle):
		self.angle += angle


class MainWindow(QMainWindow):
	def __init__(self):
		super().__init__()
		self.setGeometry(100, 100, 500, 500)
		self.angle = 0	# Initial rotation anglea
		self.setFocus()  # Enable keyboard focus

		self.truck = Truck([50.0,50.0], [100.0,60.0])

		# Create and setup the timer
		self.timer = QTimer(self)
		self.timer.timeout.connect(self.update_rotation)
		self.timer.start(16)  # 16ms = ~60 FPS

	def update_rotation(self):
		self.update()	 # Request repaint

	def paintEvent(self, event):
		painter = QPainter(self)
		painter.setRenderHint(QPainter.Antialiasing)

		self.truck.tick(0.0016)
		self.truck.drawTruck(painter)
		self.truck.drawAxles(painter)

		painter.end()

		# Increment angle for animation (optional)
		#self.angle += 1

	def keyPressEvent(self, event):
		if event.key() == Qt.Key_Up:
			self.truck.setThrottle(1)
		elif event.key() == Qt.Key_Down:
			self.truck.setThrottle(-1)
		elif event.key() == Qt.Key_Left:
			self.truck.setSteering(self.truck.getSteering()-1/36)
		elif event.key() == Qt.Key_Right:
			self.truck.setSteering(self.truck.getSteering()+1/36)

	def keyReleaseEvent(self, event):
		if event.key() == Qt.Key_Up:
			self.truck.setThrottle(0)
		elif event.key() == Qt.Key_Down:
			self.truck.setThrottle(0)
		elif event.key() == Qt.Key_Left:
			self.truck.setAngle(0)
		elif event.key() == Qt.Key_Right:
			self.truck.setAngle(0)

# Define a signal handler function
def handle_sigint(signal_received, frame):
	print("Ctrl+C pressed. Exiting the application...")
	QApplication.quit()  # Gracefully quit the application

if __name__ == '__main__':
	signal.signal(signal.SIGINT, handle_sigint)

	app = QApplication(sys.argv)
	window = MainWindow()
	window.show()
	sys.exit(app.exec_())

