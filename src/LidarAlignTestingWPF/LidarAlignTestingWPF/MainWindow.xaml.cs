using System.Diagnostics;
using System.Text;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Data;
using System.Windows.Documents;
using System.Windows.Input;
using System.Windows.Media;
using System.Windows.Media.Imaging;
using System.Windows.Navigation;
using System.Windows.Shapes;

namespace LidarAlignTestingWPF
{
    /// <summary>
    /// Interaction logic for MainWindow.xaml
    /// </summary>
    public partial class MainWindow : Window
    {
        public MainWindow()
        {
            InitializeComponent();
            Loaded += MainWindow_Loaded;
        }

        private void MainWindow_Loaded(object sender, RoutedEventArgs e)
        {
            var lidarData = PerformLidarScan();
            foreach (var ray in lidarData)
                Debug.WriteLine($"Angle: {ray.Angle:0}°, Distance: {ray.Distance:0.0}");
        }

        private List<(double Angle, double Distance)> PerformLidarScan()
        {
            int rayCount = 360;             // full 360 rays
            double angleStep = 360.0 / rayCount;
            double maxDist = 400;           // adjust to your scene size
            Vector manualOffset = new(-12, -20); // your manual offset for geometry

            // Origin = center of lidarCaster rectangle
            double originX = Canvas.GetLeft(lidarCaster) + lidarCaster.Width / 2.0;
            double originY = Canvas.GetTop(lidarCaster) + lidarCaster.Height / 2.0;
            Point origin = new Point(originX, originY);

            // Clear old rays/points
            for (int i = lidarCanvas.Children.Count - 1; i >= 0; i--)
            {
                if (lidarCanvas.Children[i] is FrameworkElement fe && fe.Tag as string == "lidarRay")
                    lidarCanvas.Children.RemoveAt(i);
            }

            // Flatten the PathGeometry into line segments with manual offset
            var segments = new List<(Point, Point)>();
            if (obstaclePath.Data != null)
            {
                var flat = obstaclePath.Data.GetFlattenedPathGeometry();
                var transform = obstaclePath.TransformToAncestor(lidarCanvas) as GeneralTransform;

                foreach (var fig in flat.Figures)
                {
                    Point start = transform.Transform(fig.StartPoint);
                    Point prev = new Point(start.X + manualOffset.X, start.Y + manualOffset.Y);

                    foreach (var seg in fig.Segments)
                    {
                        if (seg is PolyLineSegment pls)
                        {
                            foreach (var pt in pls.Points)
                            {
                                Point end = transform.Transform(pt);
                                end = new Point(end.X + manualOffset.X, end.Y + manualOffset.Y);
                                segments.Add((prev, end));
                                prev = end;
                            }
                        }
                        else if (seg is LineSegment ls)
                        {
                            Point end = transform.Transform(ls.Point);
                            end = new Point(end.X + manualOffset.X, end.Y + manualOffset.Y);
                            segments.Add((prev, end));
                            prev = end;
                        }
                    }

                    if (fig.IsClosed)
                    {
                        Point endPoint = transform.Transform(fig.StartPoint);
                        endPoint = new Point(endPoint.X + manualOffset.X, endPoint.Y + manualOffset.Y);
                        segments.Add((prev, endPoint));
                    }
                }
            }

            var rayInfo = new List<(double Angle, double Distance)>();

            // Cast rays
            for (int i = 0; i < rayCount; i++)
            {
                double angleDeg = i * angleStep;
                double angleRad = angleDeg * Math.PI / 180.0;
                Vector dir = new Vector(Math.Cos(angleRad), Math.Sin(angleRad));

                Point closestHit = new Point(origin.X + dir.X * maxDist, origin.Y + dir.Y * maxDist);
                double closestDist = maxDist;

                // Check intersection with all segments
                foreach (var seg in segments)
                {
                    if (TryRaySegmentIntersection(origin, dir, seg.Item1, seg.Item2, out double t))
                    {
                        if (t >= 0 && t < closestDist)
                        {
                            closestDist = t;
                            closestHit = new Point(origin.X + dir.X * t, origin.Y + dir.Y * t);
                        }
                    }
                }

                // Draw ray
                var line = new Line
                {
                    X1 = origin.X,
                    Y1 = origin.Y,
                    X2 = closestHit.X,
                    Y2 = closestHit.Y,
                    Stroke = Brushes.LimeGreen,
                    StrokeThickness = 1,
                    Opacity = 0.7,
                    Tag = "lidarRay"
                };
                lidarCanvas.Children.Add(line);

                // Draw hit point if any
                if (closestDist < maxDist)
                {
                    var ellipse = new Ellipse
                    {
                        Width = 3,
                        Height = 3,
                        Fill = Brushes.Orange,
                        Stroke = null,
                        Tag = "lidarRay"
                    };
                    Canvas.SetLeft(ellipse, closestHit.X - 1.5);
                    Canvas.SetTop(ellipse, closestHit.Y - 1.5);
                    lidarCanvas.Children.Add(ellipse);
                }

                // Save ray info
                rayInfo.Add((angleDeg, closestDist));
            }

            return rayInfo;
        }

        /// <summary>
        /// Computes intersection of a ray (origin + t*dir) with a segment (p1->p2)
        /// Returns t along the ray direction, or false if no intersection.
        /// </summary>
        private static bool TryRaySegmentIntersection(Point origin, Vector dir, Point p1, Point p2, out double t)
        {
            t = double.PositiveInfinity;

            Vector v1 = origin - p1;
            Vector v2 = p2 - p1;
            Vector perp = new Vector(-dir.Y, dir.X);

            double denom = Vector.Multiply(v2, perp);
            if (Math.Abs(denom) < 1e-9)
                return false; // parallel

            double u = Vector.Multiply(v1, perp) / denom;
            double tCandidate = (v2.X * v1.Y - v2.Y * v1.X) / (dir.X * v2.Y - dir.Y * v2.X);

            t = tCandidate;

            // Intersection if t >=0 (in front of ray) and u in [0,1] (on segment)
            return t >= 0 && u >= 0 && u <= 1;
        }
        
        public static IEnumerable<T> FindVisualChildren<T>(DependencyObject parent) where T : DependencyObject
        {
            if (parent == null)
                yield break;

            for (int i = 0; i < VisualTreeHelper.GetChildrenCount(parent); i++)
            {
                var child = VisualTreeHelper.GetChild(parent, i);

                if (child is T typed)
                    yield return typed;

                foreach (var descendant in FindVisualChildren<T>(child))
                    yield return descendant;
            }
        }

    }
}