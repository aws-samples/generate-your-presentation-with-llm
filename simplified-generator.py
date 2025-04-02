"""
Simplified PowerPoint Presentation Generator using Amazon Bedrock

This version is a command-line application without Streamlit dependencies.
"""

import os
import json
import uuid
import argparse
from pptx import Presentation, util
from datetime import datetime

# Import the utilities
from src.utils import generate_presentation
from src.utils import generate_bedrock_image
from src.template_mapping import template_aws1

def main():
    """Main function to parse arguments and generate the presentation"""
    parser = argparse.ArgumentParser(description='Generate a PowerPoint presentation using Amazon Bedrock')
    
    # Required arguments
    parser.add_argument('--topic', type=str, default="Benefits of cloud computing with Amazon Web Services",
                        help='Topic for the presentation')
    parser.add_argument('--slides', type=int, default=6,
                        help='Number of slides to generate (5-15)')
    
    # Optional features
    parser.add_argument('--agenda', action='store_true', default=True,
                        help='Add an agenda slide')
    parser.add_argument('--thankyou', action='store_true', default=True,
                        help='Add a thank you slide')
    parser.add_argument('--background', action='store_true', default=True,
                        help='Generate a custom background image')
    parser.add_argument('--background-prompt', type=str, 
                        default="digital presentation wallpaper, dark blue tone, uniform color, corner gradient towards orange",
                        help='Prompt for background image generation')
    
    # Image generation options
    parser.add_argument('--images', choices=['none', 'low', 'high'], default='low',
                        help='Generate images within slides (none, low, high)')
    
    # Contact information
    parser.add_argument('--name', type=str, default="J. Doe",
                        help='Your full name')
    parser.add_argument('--contact', type=str, default="j.doe@anycompany.com",
                        help='Your contact information')
    parser.add_argument('--title', type=str, default="Chief Presentation Officer",
                        help='Your job title')
    parser.add_argument('--company', type=str, default="AnyCompany",
                        help='Your company name')
    
    # Output file
    parser.add_argument('--output', type=str, default="",
                        help='Output file path (default: auto-generated)')
    
    args = parser.parse_args()
    
    # Validate arguments
    if args.slides < 5 or args.slides > 15:
        print("Number of slides must be between 5 and 15")
        return
    
    # Process arguments
    generate_bkg = args.background
    bkg_prompt = args.background_prompt if generate_bkg else ""
    
    generate_images = args.images != 'none'
    high_res_images = args.images == 'high'
    
    contact_info = {
        "full_name": args.name,
        "contact_info": args.contact,
        "title": args.title,
        "company": args.company
    }
    
    # Start timing
    start_time = datetime.now()
    print(f"Generating presentation on: {args.topic}")
    print(f"Number of slides: {args.slides}")
    
    try:
        # Generate slides
        print("Generating slide content...")
        slides = generate_presentation(args.topic, args.slides)
        print(f"Successfully generated {len(slides)} slides!")
        
        # Create PowerPoint
        output_file = create_powerpoint(
            slides, 
            args.topic, 
            generate_bkg, 
            bkg_prompt, 
            contact_info,
            args.agenda,
            args.thankyou,
            generate_images,
            high_res_images,
            args.output
        )
        
        # Calculate and display time taken
        stop_time = datetime.now()
        delta = stop_time - start_time
        print(f"Generation completed in {round(float(delta.total_seconds()))} seconds.")
        print(f"Presentation saved to: {output_file}")
        
    except Exception as e:
        print(f"Error generating presentation: {str(e)}")

def create_powerpoint(slides, topic, generate_bkg, bkg_prompt, contact_info, 
                     create_agenda, create_thankyou, generate_images, high_res_images,
                     output_path=""):
    """Create a PowerPoint presentation from the generated slides"""
    cwd = os.getcwd()
    
    # Load template and slide formats
    prs = Presentation(cwd + "/templates/pptx_base_template.pptx")
    slides_format_json = template_aws1(high_res_images=high_res_images)
    
    # Generate background if requested
    if generate_bkg:
        print('Generating background image...')
        generate_bedrock_image(
            img_prompt=bkg_prompt, 
            current_slide_format_json={"image_height": 768, "image_width": 1152},
            cwd=cwd, 
            bkg="_bkg"
        )
    
    # Process each slide
    for slide_data in slides:
        # Get slide format information
        current_slide_format = slide_data["slideFormat"]
        try:
            current_slide_format_json = slides_format_json[current_slide_format]
        except KeyError:
            print(f"Unknown slide format: {current_slide_format}. Using default format.")
            current_slide_format = "Slide with bullet points"
            current_slide_format_json = slides_format_json[current_slide_format]
        
        # Create the slide
        layout_slide_idx = current_slide_format_json["layout_slide"]
        slide_layout = prs.slide_layouts[layout_slide_idx]
        slide = prs.slides.add_slide(slide_layout)
        
        # Add speaker notes
        notes_slide = slide.notes_slide
        text_frame = notes_slide.notes_text_frame
        text_frame.text = json.dumps(slide_data, indent=4)
        
        print(f"Creating slide {slide_data['slide_n']}: {slide_data['title']} ({current_slide_format})")
        
        # Add content based on slide format
        if current_slide_format == "Title page":
            # Add title and subtitle
            title = slide.placeholders[current_slide_format_json["title_placeholder"]]
            title.text = slide_data["title"]
            
            subtitle = slide.placeholders[current_slide_format_json["subtitle_placeholder"]]
            subtitle.text = slide_data["subtitle"]
            
            # Add contact information if provided
            if contact_info:
                full_name = slide.placeholders[current_slide_format_json["full_name_placeholder"]]
                full_name.text = contact_info["full_name"]
                
                job_title = slide.placeholders[current_slide_format_json["job_title_placeholder"]]
                job_title.text = f"{contact_info['title']}\n{contact_info['company']}"
                
            # Add background image if generated
            if generate_bkg:
                left = top = util.Inches(0)
                bkg_img_path = "/tmp/test_image_bkg.jpg"
                pic = slide.shapes.add_picture(cwd+bkg_img_path, left, top, width=prs.slide_width, height=prs.slide_height)
                cursor_sp = slide.shapes[0]._element
                cursor_sp.addprevious(pic._element)
        
        elif current_slide_format == "Slide with bullet points":
            # Add title and subtitle
            title = slide.placeholders[current_slide_format_json["title_placeholder"]]
            title.text = slide_data["title"]
            
            subtitle = slide.placeholders[current_slide_format_json["subtitle_placeholder"]]
            subtitle.text = slide_data["subtitle"]
            
            # Add bullet points
            main_text = slide.placeholders[current_slide_format_json["text_placeholder"]]
            main_text.text = slide_data.get("text").replace("*** ", "\n").replace("- ", "").strip()
        
        elif current_slide_format in ["Slide with image and text", "Slide with image only"]:
            # Add title
            title = slide.placeholders[current_slide_format_json["title_placeholder"]]
            title.text = slide_data["title"]
            
            # Add text if applicable
            if current_slide_format == "Slide with image and text":
                main_text = slide.placeholders[current_slide_format_json["text_placeholder"]]
                main_text.text = slide_data.get("text").replace("*** ", "\n").replace("- ", "").strip()
            
            # Add image if requested
            if generate_images:
                image_placeholder = slide.placeholders[current_slide_format_json["image_placeholder"]]
                content_for_image = slide_data["title"] + " " + slide_data.get("text", "")
                img_prompt = f"Create an abstract image representing: {content_for_image[:100]}"
                
                print(f"Generating image for slide {slide_data['slide_n']}...")
                generate_bedrock_image(
                    img_prompt=img_prompt, 
                    current_slide_format_json=current_slide_format_json,
                    image_placeholder=image_placeholder, 
                    cwd=cwd
                )
        
        elif current_slide_format == "Slide with 4 takeaways":
            # Add title
            title = slide.placeholders[current_slide_format_json["title_placeholder"]]
            title.text = slide_data["title"]
            
            # Add takeaways
            four_options = slide_data.get("text").split("***")
            four_options = [opt for opt in four_options if opt.strip()]
            
            for i, text_opt in enumerate(four_options[:4]):
                text_opt_placeholder = slide.placeholders[current_slide_format_json[f"text{i+1}_placeholder"]]
                text_opt_placeholder.text = text_opt.strip()
    
    # Add agenda slide if requested
    if create_agenda:
        # Create an agenda slide with titles from all content slides
        print("Creating agenda slide...")
        agenda_slide_layout = prs.slide_layouts[slides_format_json["Agenda"]["layout_slide"]]
        agenda_slide = prs.slides.add_slide(agenda_slide_layout)
        
        # Add title
        title = agenda_slide.placeholders[slides_format_json["Agenda"]["title_placeholder"]]
        title.text = "Agenda"
        
        # Create agenda text from slide titles
        agenda_text = "\n".join([f"• {slide['title']}" for slide in slides if slide["slideFormat"] != "Title page"])
        
        # Add agenda text
        main_text = agenda_slide.placeholders[slides_format_json["Agenda"]["text_placeholder"]]
        main_text.text = agenda_text
    
    # Add thank you slide if requested
    if create_thankyou:
        # Create a thank you slide
        print("Creating thank you slide...")
        thank_you_layout = prs.slide_layouts[slides_format_json["Thank you"]["layout_slide"]]
        thank_you_slide = prs.slides.add_slide(thank_you_layout)
        
        # Add title
        title = thank_you_slide.placeholders[slides_format_json["Thank you"]["title_placeholder"]]
        title.text = "Thank you!"
        
        # Add contact information if provided
        if contact_info:
            try:
                full_name = thank_you_slide.placeholders[slides_format_json["Thank you"]["full_name_placeholder"]]
                full_name.text = contact_info["full_name"]
                
                contact_text = thank_you_slide.placeholders[slides_format_json["Thank you"]["contact_info_placeholder"]]
                contact_text.text = contact_info["contact_info"]
            except:
                print("Could not add all contact information to thank you slide")
        
        # Add background image if generated
        if generate_bkg:
            left = top = util.Inches(0)
            bkg_img_path = "/tmp/test_image_bkg.jpg"
            pic = thank_you_slide.shapes.add_picture(cwd+bkg_img_path, left, top, width=prs.slide_width, height=prs.slide_height)
            cursor_sp = thank_you_slide.shapes[0]._element
            cursor_sp.addprevious(pic._element)
    
    # Save the presentation
    if output_path:
        output_file = output_path
    else:
        output_file = cwd + '/output/output_' + str(uuid.uuid4()) + '.pptx'
    
    prs.save(output_file)
    return output_file

if __name__ == "__main__":
    main()
