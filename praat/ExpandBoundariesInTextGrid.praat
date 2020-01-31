form Move left boundary earlier and right later
	comment Specify tier to be processed:
	integer tier 1
	comment Specify number of milliseconds to move boundaries by:
	positive moveDurIzq 120
	positive moveDurDer 0
endform

moveDurIzq = moveDurIzq/1000
moveDurDer = moveDurDer/1000

# soundname$ = selected$ ("Sound", 1)
textgrid$ = selected$ ("TextGrid", 1)

#########################
# Primero el izquierdo
#########################

writeInfoLine: "Boundaries moved for the following labeled intervals:'newline$'"


select TextGrid 'textgrid$'

      #check if specified tier is interval tier
      interval = Is interval tier... tier
      
      # Process intervals
      if interval 
         ni = Get number of intervals... tier
         for i to ni
          	label$[i] = Get label of interval... tier i
         endfor

             for i to ni
             select TextGrid 'textgrid$'
		  
		  #if interval is labeled
		  if label$[i] = ""
		  elsif label$[i] = " "
		  elsif label$[i] = newline$
		  else
		  appendInfoLine: label$[i]

			#move left boundary earlier by specified duration
			select TextGrid 'textgrid$'
			leftbound = Get start point... tier i
			appendInfoLine: "original boundaries:'leftbound', 'boundary'"
			Insert boundary... tier leftbound - moveDurIzq
			Remove right boundary... tier i
						
			
		  endif
endfor

        select TextGrid 'textgrid$'
        for i to ni
          name$ = label$[i]
          Set interval text... tier i 'name$'
        endfor



#########################
# Luego el derecho
#########################

select TextGrid 'textgrid$'

      #check if specified tier is interval tier
      interval = Is interval tier... tier
      
      # Process intervals
      if interval 
         ni = Get number of intervals... tier
         for i to ni
          	label$[i] = Get label of interval... tier i
         endfor

             for i to ni
             select TextGrid 'textgrid$'
		  
		  #if interval is labeled
		  if label$[i] = ""
		  elsif label$[i] = " "
		  elsif label$[i] = newline$
		  else
		  appendInfoLine: label$[i]
            
		    
			#move right boundary later by specified duration
			select TextGrid 'textgrid$'
			rightbound = Get end point... tier i
			Remove right boundary... tier i
			Insert boundary... tier rightbound + moveDurDer
						
			select TextGrid 'textgrid$'
			a = Get start point... tier i
			b = Get end point... tier i
			appendInfoLine: "new boundaries: 'a', 'b''newline$'"
			
		  endif
               endfor

        select TextGrid 'textgrid$'
        for i to ni
          name$ = label$[i]
          Set interval text... tier i 'name$'
        endfor

