package com.nantic.jasperreports;

import java.util.Iterator;
import java.util.ArrayList;

import java.io.PrintStream;
import net.sf.jasperreports.engine.JasperCompileManager;

public class I18nGetText {
	public static void main (String [] args) {
		if ( args.length != 1 ) {
			System.out.println( "Syntax: I18nGetText filename.jrxml" );
			System.exit(1);
		}
		String fileName = args[0];

		System.setProperty("jasper.reports.compiler.class", "com.nantic.jasperreports.I18nGroovyCompiler");

		try {
			I18nGroovyCompiler.sourceCodeList = new ArrayList();
			JasperCompileManager.compileReport( fileName );
			//System.out.println( I18nGroovyCompiler.lastGeneratedSourceCode );
			PrintStream out = new PrintStream(System.out, true, "UTF-8");
			Iterator<String> iterator = I18nGroovyCompiler.sourceCodeList.iterator();
			while ( iterator.hasNext() ) {
				out.println( iterator.next() );
			}
			System.exit(0);

		} catch (Exception e) {
			System.out.println( "Error compiling report: " + e.getMessage() );
			System.exit(2);
		}
	}
}
