package main

import (
	"fmt"
	"image"
	"image/png"
	"log"
	"os"
	"os/exec"
	"os/signal"
	"path/filepath"
	"syscall"
	"time"

	"github.com/fogleman/gg"
	"github.com/kbinani/screenshot"
	"github.com/spf13/pflag"
)

type Config struct {
	Interval   time.Duration
	Text       string
	FPS        int
	OutputDir  string
	FontSize   float64
}

func main() {
	// Parse command line arguments
	config := parseFlags()

	// Create output directory
	if err := os.MkdirAll(config.OutputDir, 0755); err != nil {
		log.Fatalf("Erreur lors de la création du répertoire de sortie: %v", err)
	}

	// Get number of monitors
	numMonitors := screenshot.NumActiveDisplays()
	if numMonitors == 0 {
		log.Fatal("Aucun moniteur détecté")
	}

	fmt.Printf("Détection de %d moniteur(s)\n", numMonitors)
	fmt.Printf("Intervalle de capture: %v\n", config.Interval)
	fmt.Printf("Texte à afficher: %s\n", config.Text)
	fmt.Printf("FPS de la vidéo: %d\n", config.FPS)
	fmt.Println("Appuyez sur Ctrl+C pour arrêter...")

	// Setup signal handling for graceful shutdown
	sigChan := make(chan os.Signal, 1)
	signal.Notify(sigChan, os.Interrupt, syscall.SIGTERM)

	// Create channels for each monitor
	done := make(chan bool)
	
	// Start capture goroutines for each monitor
	for i := 0; i < numMonitors; i++ {
		go captureMonitor(i, config, done)
	}

	// Wait for interrupt signal
	<-sigChan
	fmt.Println("\n\nArrêt de la capture...")
	
	// Signal all goroutines to stop
	for i := 0; i < numMonitors; i++ {
		done <- true
	}

	// Wait a bit for cleanup
	time.Sleep(1 * time.Second)

	// Create videos from captured images
	fmt.Println("\nCréation des vidéos...")
	for i := 0; i < numMonitors; i++ {
		createVideo(i, config)
	}

	fmt.Println("Terminé!")
}

func parseFlags() Config {
	interval := pflag.IntP("interval", "i", 5, "Intervalle entre les captures en secondes")
	text := pflag.StringP("text", "t", "", "Texte à afficher au centre de l'image (requis)")
	fps := pflag.IntP("fps", "f", 5, "Frame rate (FPS) de la vidéo de sortie")
	outputDir := pflag.StringP("output", "o", "./output", "Répertoire de sortie pour les vidéos")
	fontSize := pflag.Float64P("fontsize", "s", 48.0, "Taille de la police pour le texte")
	
	pflag.Parse()

	if *text == "" {
		fmt.Println("Erreur: Le paramètre --text/-t est requis")
		pflag.Usage()
		os.Exit(1)
	}

	return Config{
		Interval:   time.Duration(*interval) * time.Second,
		Text:       *text,
		FPS:        *fps,
		OutputDir:  *outputDir,
		FontSize:   *fontSize,
	}
}

func captureMonitor(monitorID int, config Config, done chan bool) {
	bounds := screenshot.GetDisplayBounds(monitorID)
	imageDir := filepath.Join(config.OutputDir, fmt.Sprintf("monitor_%d", monitorID))
	
	if err := os.MkdirAll(imageDir, 0755); err != nil {
		log.Printf("Erreur lors de la création du répertoire pour le moniteur %d: %v", monitorID, err)
		return
	}

	frameCount := 0
	ticker := time.NewTicker(config.Interval)
	defer ticker.Stop()

	for {
		select {
		case <-done:
			fmt.Printf("Moniteur %d: %d images capturées\n", monitorID, frameCount)
			return
		case <-ticker.C:
			// Capture screenshot
			img, err := screenshot.CaptureRect(bounds)
			if err != nil {
				log.Printf("Erreur lors de la capture du moniteur %d: %v", monitorID, err)
				continue
			}

			// Add text overlay
			imgWithText := addTextOverlay(img, config.Text, config.FontSize)

			// Save image
			filename := filepath.Join(imageDir, fmt.Sprintf("frame_%05d.png", frameCount))
			if err := saveImage(imgWithText, filename); err != nil {
				log.Printf("Erreur lors de la sauvegarde de l'image: %v", err)
				continue
			}

			frameCount++
			fmt.Printf("Moniteur %d: Frame %d capturé\n", monitorID, frameCount)
		}
	}
}

func addTextOverlay(img *image.RGBA, text string, fontSize float64) *image.RGBA {
	// Create a new context with the image
	dc := gg.NewContextForRGBA(img)

	// Set font
	if err := dc.LoadFontFace("C:\\Windows\\Fonts\\arial.ttf", fontSize); err != nil {
		// Try alternative font paths for different OS
		if err := dc.LoadFontFace("/System/Library/Fonts/Helvetica.ttc", fontSize); err != nil {
			if err := dc.LoadFontFace("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", fontSize); err != nil {
				// If no font found, use default (will be basic)
				log.Printf("Avertissement: Impossible de charger une police, texte non ajouté: %v", err)
				return img
			}
		}
	}

	// Calculate text position (center)
	w := float64(img.Bounds().Dx())
	h := float64(img.Bounds().Dy())
	
	// Draw text with shadow for better visibility
	// Shadow
	dc.SetRGB(0, 0, 0)
	dc.DrawStringAnchored(text, w/2+2, h/2+2, 0.5, 0.5)
	
	// Main text (white)
	dc.SetRGB(1, 1, 1)
	dc.DrawStringAnchored(text, w/2, h/2, 0.5, 0.5)

	return dc.Image().(*image.RGBA)
}

func saveImage(img *image.RGBA, filename string) error {
	file, err := os.Create(filename)
	if err != nil {
		return err
	}
	defer file.Close()

	return png.Encode(file, img)
}

func createVideo(monitorID int, config Config) {
	imageDir := filepath.Join(config.OutputDir, fmt.Sprintf("monitor_%d", monitorID))
	outputVideo := filepath.Join(config.OutputDir, fmt.Sprintf("monitor_%d.mp4", monitorID))

	// Check if ffmpeg is available
	if _, err := exec.LookPath("ffmpeg"); err != nil {
		fmt.Printf("AVERTISSEMENT: FFmpeg n'est pas installé. Les images sont sauvegardées dans %s\n", imageDir)
		fmt.Println("Pour créer la vidéo manuellement, installez FFmpeg et exécutez:")
		fmt.Printf("  ffmpeg -framerate %d -i %s/frame_%%05d.png -c:v libx264 -preset medium -crf 23 -pix_fmt yuv420p %s\n", 
			config.FPS, imageDir, outputVideo)
		return
	}

	// Create video using ffmpeg with H.264 compression
	// -crf 23 is default quality (lower = better quality, range 0-51)
	// -preset medium is encoding speed (slower = better compression)
	cmd := exec.Command("ffmpeg",
		"-framerate", fmt.Sprintf("%d", config.FPS),
		"-i", filepath.Join(imageDir, "frame_%05d.png"),
		"-c:v", "libx264",
		"-preset", "medium",
		"-crf", "23",
		"-pix_fmt", "yuv420p",
		"-y", // Overwrite output file
		outputVideo,
	)

	output, err := cmd.CombinedOutput()
	if err != nil {
		log.Printf("Erreur lors de la création de la vidéo pour le moniteur %d: %v\n%s", monitorID, err, output)
		return
	}

	fmt.Printf("Vidéo créée: %s\n", outputVideo)

	// Optionally, remove the images after creating the video
	// Uncomment the following lines if you want to delete the source images:
	// if err := os.RemoveAll(imageDir); err != nil {
	// 	log.Printf("Erreur lors de la suppression des images: %v", err)
	// }
}
