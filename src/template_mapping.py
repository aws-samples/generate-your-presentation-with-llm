
def template_aws1(high_res_images = False):
    if high_res_images:
        image_size_long = 1152
        image_size_short = 768
    else:
        image_size_long = 576
        image_size_short = 384
        
    return {
                "Title page":{
                                "layout_slide": 0, 
                                "title_placeholder": 0,
                                "subtitle_placeholder": 1,
                                "full_name_placeholder": 11,
                                "job_title_placeholder": 12,
                                "text_placeholder": 2
                                },
                "Agenda":{
                                "layout_slide": 1, 
                                "title_placeholder": 0,
                                "agenda_title": "Today's agenda",
                                "text_placeholder": 10
                                },
                "Slide with bullet points":{
                                "layout_slide": 2,
                                "title_placeholder": 0,
                                "subtitle_placeholder": 10,
                                "text_placeholder": 1
                                },
                "Slide with image and text":{
                                "layout_slide": 3,
                                "title_placeholder": 0,
                                "text_placeholder": 1,
                                "image_text_field": "text",
                                "image_placeholder": 10,
                                "image_height": image_size_long,
                                "image_width": image_size_short
                                },
                "Slide with image only":{
                                "layout_slide": 4,
                                "image_placeholder": 10,
                                "image_text_field": "title",
                                "image_height": image_size_short,
                                "image_width": image_size_long
                                },
                "Slide with 4 takeaways":{
                                "layout_slide": 5,
                                "title_placeholder": 0,
                                "text1_placeholder": 17,
                                "text2_placeholder": 18,
                                "text3_placeholder": 19,
                                "text4_placeholder": 20,
                                },
                "Thank you":{
                                "layout_slide": 6, 
                                "title_placeholder": 0,
                                "full_name_placeholder": 10,
                                "contact_info_placeholder": 11
                                }
                 }