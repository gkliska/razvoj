/*
 * Capslock 0.3 - jQuery plugin to detect if a user's caps lock is on or not.
 * 
 * Provides events, "caps_lock_on" and "caps_lock_off", that custom functions can be bound to.
 * The capslock function can be called on a specific element, or a set of elements:
 * 		$("#my_textarea").capslock(options);	// One textarea
 * 		$("textarea").capslock(options);		// All textareas
 *
 * Copyright (c) 2009 Arthur McLean
 *
 * Dual licensed under the MIT and GPL licenses:
 *   http://www.opensource.org/licenses/mit-license.php
 *   http://www.gnu.org/licenses/gpl.html
 *
 */

; // Just in case the previously included plug-in failed to close with a semi-colon.
(function($) {
	
	$.fn.capslock = function(options) {
		
		if (options) $.extend($.fn.capslock.defaults, options);
		
		this.each(function() {
			$(this).bind("caps_lock_on", $.fn.capslock.defaults.caps_lock_on);
			$(this).bind("caps_lock_off", $.fn.capslock.defaults.caps_lock_off);
			
			$(this).keypress(function(e){
				check_caps_lock(e);
			});
		});
		
		return this;
	};
	

	
	// The actual check:
	function check_caps_lock(e) {
		
		var ascii_code	= e.which;
		var letter = String.fromCharCode(ascii_code);
		var upper = letter.toUpperCase();
		var shift_key	= e.shiftKey;
		
		if(
			($.inArray(ascii_code, $.fn.capslock.defaults.ascii_exceptions) === -1)
			&&
			(letter === upper)
			&&
			!shift_key
		) {
			$(e.target).trigger("caps_lock_on");
		} else {
			$(e.target).trigger("caps_lock_off");
		}
		
		/*
		if( (65 <= ascii_code) && (ascii_code <= 90) && !shift_key) {
			$(e.target).trigger("caps_lock_on");
		} else {
			$(e.target).trigger("caps_lock_off");
		}
		*/
		
		if($.fn.capslock.defaults.debug) {
			if(console) {
				console.log("Ascii code: " + ascii_code);
				console.log("Letter: " + letter);
				console.log("Upper Case: " + upper);
				console.log("Shift key: " + shift_key);
			}
		}
		
	}
	
	// Public definition of defaults for easy overriding:
	$.fn.capslock.defaults = {
		caps_lock_on:	function() {},
		caps_lock_off:	function() {},
		debug:			false,
		ascii_exceptions: [
			0,		// Null char
			1,		// Start of Heading
			2,		// Start of Text
			3,		// End of Text
			4,		// End of Transmission
			5,		// Enquiry
			6,		// Acknowledgment
			7,		// Bell
			8,		// Back Space
			9,		// Horizontal Tab
			10,		// Line Feed
			11,		// Vertical Tab
			12,		// Form Feed
			13,		// Carriage Return
			14,		// Shift Out / X-On
			15,		// Shift In / X-Off
			16,		// Data Line Escape
			17,		// Device Control 1 (oft. XON)
			18,		// Device Control 2
			19,		// Device Control 3 (oft. XOFF)
			20,		// Device Control 4
			21,		// Negative Acknowledgement
			22,		// Synchronous Idle
			23,		// End of Transmit Block
			24,		// Cancel
			25,		// End of Medium
			26,		// Substitute
			27,		// Escape
			28,		// File Separator
			29,		// Group Separator
			30,		// Record Separator
			31,		// Unit Separator
			32,		// Space
			33,		// Exclamation mark
			34,		// Double quotes (or speech marks)
			35,		// Number
			36,		// Dollar
			37,		// Procenttecken
			38,		// Ampersand
			39,		// Single quote
			40,		// Open parenthesis (or open bracket)
			41,		// Close parenthesis (or close bracket)
			42,		// Asterisk
			43,		// Plus
			44,		// Comma
			45,		// Hyphen
			46,		// Period, dot or full stop
			47,		// Slash or divide
			48,		// Zero
			49,		// One
			50,		// Two
			51,		// Three
			52,		// Four
			53,		// Five
			54,		// Six
			55,		// Seven
			56,		// Eight
			57,		// Nine
			58,		// Colon
			59,		// Semicolon
			60,		// Less than (or open angled bracket)
			61,		// Equals
			62,		// Greater than (or close angled bracket)
			63,		// Question mark
			64,		// At symbol
			91,		// Opening bracket
			92,		// Backslash
			93,		// Closing bracket
			94,		// Caret - circumflex
			95,		// Underscore
			96,		// Grave accent
			123,	// Opening brace
			124,	// Vertical bar
			125,	// Closing brace
			126,	// Equivalency sign - tilde
			127,	// Delete
			128,	// Euro sign
			129,	// Unassigned?	 	 	 	 
			130,	// Single low-9 quotation mark
			132,	// Double low-9 quotation mark
			133,	// Horizontal ellipsis
			134,	// Dagger
			135,	// Double dagger
			136,	// Modifier letter circumflex accent
			137,	// Per mille sign
			139,	// Single left-pointing angle quotation
			141,	// Unassigned?	
			143,	// Unassigned?	 	 	 	 
			144,	// Unassigned?	 	 	 	 
			145,	// Left single quotation mark
			146,	// Right single quotation mark
			147,	// Left double quotation mark
			148,	// Right double quotation mark
			149,	// Bullet
			150,	// En dash
			151,	// Em dash
			152,	// Small tilde
			153,	// Trade mark sign
			155,	// Single right-pointing angle quotation mark
			157,	// Unassigned?	
			160,	// Non-breaking space
			161,	// Inverted exclamation mark
			162,	// Cent sign
			163,	// Pound sign
			164,	// Currency sign
			165,	// Yen sign
			166,	// Pipe, Broken vertical bar
			167,	// Section sign
			168,	// Spacing diaeresis - umlaut
			169,	// Copyright sign
			170,	// Feminine ordinal indicator
			171,	// Left double angle quotes
			172,	// Not sign
			173,	// Soft hyphen
			174,	// Registered trade mark sign
			175,	// Spacing macron - overline
			176,	// Degree sign
			177,	// Plus-or-minus sign
			178,	// Superscript two - squared
			179,	// Superscript three - cubed
			180,	// Acute accent - spacing acute
			181,	// Micro sign
			182,	// Pilcrow sign - paragraph sign
			183,	// Middle dot - Georgian comma
			184,	// Spacing cedilla
			185,	// Superscript one
			186,	// Masculine ordinal indicator
			187,	// Right double angle quotes
			188,	// Fraction one quarter
			189,	// Fraction one half
			190,	// Fraction three quarters
			191,	// Inverted question mark
			215,	// Multiplication sign
			247		// Division sign
		]
	};
	
})(jQuery);

